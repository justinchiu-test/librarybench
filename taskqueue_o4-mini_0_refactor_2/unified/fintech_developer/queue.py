import time
from fintech_developer.quota import QuotaExceeded
from fintech_developer.tenant import TenantContext, MultiTenancySupport
from fintech_developer.circuit_breaker import CircuitOpen
from threading import Lock

class TaskQueue:
    def __init__(self, metrics, quota, tenancy, circuit_breaker, audit, scheduler, encryption):
        self.metrics = metrics
        self.quota = quota
        self.tenancy = tenancy
        self.circuit = circuit_breaker
        self.audit = audit
        self.scheduler = scheduler
        self.encryption = encryption
        self.failed_tasks = []
        self._lock = Lock()

    def enqueue(self, payment_type, amount, merchant_id, customer_id, tenant_id, binary_payload=None, delay_until=None):
        # Tenant context
        with TenantContext(tenant_id):
            # Register or verify resource
            self.tenancy.register_resource(merchant_id, tenant_id)
            self.tenancy.register_resource(customer_id, tenant_id)
            # Quota
            self.quota.check_and_consume(merchant_id, customer_id, amount)
            # Audit
            self.audit.log(tenant_id, "enqueue", {
                "payment_type": payment_type,
                "amount": amount,
                "merchant_id": merchant_id,
                "customer_id": customer_id
            })
            # Metrics
            self.metrics.record_throughput(payment_type)
            # Encrypted payload
            if binary_payload is not None:
                encrypted = self.encryption.encrypt(binary_payload)
            else:
                encrypted = None

            def _process():
                try:
                    self._process_task(payment_type, tenant_id, encrypted)
                except Exception as e:
                    self.audit.log(tenant_id, "task_failed", {"error": str(e)})
                    self.metrics.record_failure(payment_type)
                    with self._lock:
                        self.failed_tasks.append({
                            "payment_type": payment_type,
                            "tenant_id": tenant_id,
                            "error": str(e)
                        })
                    # propagate to caller/scheduler
                    raise

            if delay_until:
                run_at = delay_until
                self.scheduler.schedule(run_at, _process)
            else:
                # process immediately, propagating exceptions
                _process()

    def _fake_fraud_api(self, payment_type):
        # Always returns True for simplicity
        return True

    def _process_task(self, payment_type, tenant_id, encrypted_payload):
        # Fraud check
        self.audit.log(tenant_id, "fraud_check_start", {"payment_type": payment_type})
        try:
            result = self.circuit.call(self._fake_fraud_api, payment_type)
        except CircuitOpen:
            self.audit.log(tenant_id, "fraud_check_blocked", {"payment_type": payment_type})
            raise
        except Exception as e:
            self.audit.log(tenant_id, "fraud_check_failed", {"error": str(e)})
            raise
        else:
            self.audit.log(tenant_id, "fraud_check_pass", {"result": result})
        # Risk scoring
        self.audit.log(tenant_id, "risk_score", {"score": 0})
        # Ledger update
        self.audit.log(tenant_id, "ledger_update", {"status": "settled"})
        # Final audit
        self.audit.log(tenant_id, "settlement_complete", {"payment_type": payment_type})

    def queue_health(self):
        return {
            "failed_tasks": list(self.failed_tasks),
            "pending_tasks": len(self.scheduler._queue)
        }

    def replay_failed(self):
        with self._lock:
            to_replay = list(self.failed_tasks)
            self.failed_tasks.clear()
        for task in to_replay:
            # naive replay: just log replay
            tenant_id = task["tenant_id"]
            self.audit.log(tenant_id, "replay_task", task)
        return to_replay
