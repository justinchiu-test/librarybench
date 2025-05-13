import argparse
import time
from metrics import MetricsIntegration
from quota import QuotaManagement
from tenant import MultiTenancySupport
from circuit_breaker import CircuitBreaker
from audit import AuditLogger
from scheduler import Scheduler
from encryption import EncryptionManager
from queue import TaskQueue

def build_system():
    metrics = MetricsIntegration()
    quota = QuotaManagement()
    tenancy = MultiTenancySupport()
    circuit = CircuitBreaker()
    audit = AuditLogger()
    scheduler = Scheduler()
    encryption = EncryptionManager(key=b'secretkey')
    queue = TaskQueue(metrics, quota, tenancy, circuit, audit, scheduler, encryption)
    return queue, scheduler

def cmd_test_transaction(args):
    queue, scheduler = build_system()
    queue.enqueue(
        payment_type=args.type,
        amount=args.amount,
        merchant_id=args.merchant,
        customer_id=args.customer,
        tenant_id=args.tenant,
        binary_payload=b"test"
    )
    scheduler.run_due()
    print("Transaction processed")

def cmd_queue_health(args):
    queue, _ = build_system()
    health = queue.queue_health()
    print(health)

def cmd_replay_failed(args):
    queue, _ = build_system()
    replayed = queue.replay_failed()
    print(f"Replayed {len(replayed)} tasks")

def main():
    parser = argparse.ArgumentParser(description="Payment CLI")
    sub = parser.add_subparsers(dest="command")
    p1 = sub.add_parser("test_transaction")
    p1.add_argument("--tenant", required=True)
    p1.add_argument("--merchant", required=True)
    p1.add_argument("--customer", required=True)
    p1.add_argument("--amount", type=int, required=True)
    p1.add_argument("--type", required=True)
    p2 = sub.add_parser("queue_health")
    p3 = sub.add_parser("replay_failed")
    args = parser.parse_args()
    if args.command == "test_transaction":
        cmd_test_transaction(args)
    elif args.command == "queue_health":
        cmd_queue_health(args)
    elif args.command == "replay_failed":
        cmd_replay_failed(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
