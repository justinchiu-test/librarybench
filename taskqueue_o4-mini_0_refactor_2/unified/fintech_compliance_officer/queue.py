import time
import json
import uuid
from fintech_compliance_officer.encryption import encrypt, decrypt

class TaskQueue:
    def __init__(self, encryption_key, max_retries=3):
        self.encryption_key = encryption_key
        self.max_retries = max_retries
        self.tasks = []  # list of task dicts
        self.dead_letters = []
        self.audit_log = []
        self.metrics = {
            'throughput': 0,
            'failures': 0,
            'retries': 0,
            'latencies': []
        }
        self.in_flight = set()
        self.shutdown_flag = False

    def enqueue(self, payload, delay=0):
        task_id = str(uuid.uuid4())
        encrypted_payload = encrypt(json.dumps(payload), self.encryption_key)
        scheduled_time = time.time() + delay
        task = {
            'id': task_id,
            'encrypted_payload': encrypted_payload,
            'scheduled_time': scheduled_time,
            'retries': 0,
            'status': 'queued'
        }
        self.tasks.append(task)
        self._audit('enqueue', task_id, {'delay': delay})
        return task_id

    def process_next(self):
        if self.shutdown_flag:
            return None
        now = time.time()
        for task in self.tasks:
            if task['status'] == 'queued' and task['scheduled_time'] <= now:
                task_id = task['id']
                task['status'] = 'in-flight'
                self.in_flight.add(task_id)
                start = time.time()
                try:
                    data = decrypt(task['encrypted_payload'], self.encryption_key)
                    payload = json.loads(data)
                    time.sleep(0)
                    task['status'] = 'completed'
                    self.metrics['throughput'] += 1
                    latency = time.time() - start
                    self.metrics['latencies'].append(latency)
                    self._audit('complete', task_id, {})
                except Exception as e:
                    self._handle_failure(task, e)
                finally:
                    self.in_flight.discard(task_id)
                return task
        return None

    def _handle_failure(self, task, exception):
        task['retries'] += 1
        self.metrics['retries'] += 1
        self._audit('retry', task['id'], {'error': str(exception), 'retry': task['retries']})
        if task['retries'] > self.max_retries:
            task['status'] = 'dead'
            self.dead_letters.append(task)
            self.metrics['failures'] += 1
            self._audit('dead_letter', task['id'], {})
        else:
            task['status'] = 'queued'

    def retry_task(self, task_id):
        for task in self.tasks:
            if task['id'] == task_id:
                self._handle_failure(task, Exception('manual retry'))
                return True
        return False

    def cancel_task(self, task_id):
        for task in self.tasks:
            if task['id'] == task_id and task['status'] in ('queued',):
                task['status'] = 'cancelled'
                self._audit('cancel', task_id, {})
                return True
        return False

    def get_metrics(self):
        return self.metrics.copy()

    def _audit(self, event_type, task_id, details):
        self.audit_log.append({
            'timestamp': time.time(),
            'task_id': task_id,
            'event': event_type,
            'details': details
        })

    def backup(self):
        state = {
            'tasks': [task.copy() for task in self.tasks],
            'dead_letters': [task.copy() for task in self.dead_letters],
            'audit_log': [entry.copy() for entry in self.audit_log],
            'metrics': self.metrics.copy()
        }
        return state

    def restore(self, state):
        self.tasks = [task.copy() for task in state.get('tasks', [])]
        self.dead_letters = [task.copy() for task in state.get('dead_letters', [])]
        self.audit_log = [entry.copy() for entry in state.get('audit_log', [])]
        self.metrics = state.get('metrics', {}).copy()

    def shutdown(self):
        self.shutdown_flag = True

    def get_dead_letter_queue(self):
        return list(self.dead_letters)

    def get_audit_log(self):
        return list(self.audit_log)

    def peek_queue(self):
        result = []
        for task in self.tasks:
            data = decrypt(task['encrypted_payload'], self.encryption_key)
            payload = json.loads(data)
            result.append({
                'id': task['id'],
                'payload': payload,
                'scheduled_time': task['scheduled_time'],
                'retries': task['retries'],
                'status': task['status']
            })
        return result
