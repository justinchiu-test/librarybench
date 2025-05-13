import time
import threading
import uuid
import pickle
import os

# Encryption at rest using simple XOR cipher for demonstration
def _xor_encrypt(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

def _xor_decrypt(data: bytes, key: bytes) -> bytes:
    return _xor_encrypt(data, key)  # symmetric

class Task:
    def __init__(self, payload, eta=None, max_retries=3):
        self.id = str(uuid.uuid4())
        self.payload = payload
        self.eta = eta or time.time()
        self.retries = 0
        self.max_retries = max_retries
        self.status = 'pending'

class TaskQueue:
    def __init__(self, data_dir='.', encryption_key=b'secret'):
        self.data_dir = data_dir
        self.key = encryption_key
        self.tasks = []
        self.dlq = []
        self.metrics = {
            'processed': 0,
            'failed': 0,
            'retries': 0,
            'enqueued': 0,
            'canceled': 0,
            'dlq': 0,
        }
        self.audit_log_path = os.path.join(self.data_dir, 'audit.log')
        self._lock = threading.Lock()
        self._accepting = True

    def _log_audit(self, event_type, task):
        entry = f'{time.time()},{event_type},{task.id}\n'.encode()
        # Figure out current file size so we continue the XOR key offset
        try:
            offset = os.path.getsize(self.audit_log_path)
        except OSError:
            offset = 0
        # Encrypt entry bytes with a rolling key offset
        enc = bytes(
            b ^ self.key[(offset + i) % len(self.key)]
            for i, b in enumerate(entry)
        )
        with open(self.audit_log_path, 'ab') as f:
            f.write(enc)

    def enqueue(self, payload, eta=None, delay=None, max_retries=None):
        with self._lock:
            if not self._accepting:
                raise RuntimeError('Queue not accepting new tasks')
            if delay is not None:
                eta = time.time() + delay
            task = Task(payload, eta, max_retries or 3)
            self.tasks.append(task)
            self.metrics['enqueued'] += 1
            self._log_audit('enqueue', task)
            return task.id

    def cancel(self, task_id):
        with self._lock:
            for t in list(self.tasks):
                if t.id == task_id and t.status == 'pending':
                    self.tasks.remove(t)
                    t.status = 'canceled'
                    self.metrics['canceled'] += 1
                    self._log_audit('cancel', t)
                    return True
            return False

    def get_ready_tasks(self):
        now = time.time()
        return [t for t in self.tasks if t.status == 'pending' and t.eta <= now]

    def dequeue(self):
        with self._lock:
            ready = self.get_ready_tasks()
            if not ready:
                return None
            task = ready[0]
            task.status = 'running'
            self._log_audit('dequeue', task)
            return task

    def finish(self, task):
        with self._lock:
            task.status = 'finished'
            self.metrics['processed'] += 1
            self._log_audit('finish', task)

    def fail(self, task):
        with self._lock:
            task.retries += 1
            self.metrics['retries'] += 1
            self._log_audit('retry', task)
            if task.retries > task.max_retries:
                task.status = 'failed'
                self.dlq.append(task)
                self.metrics['dlq'] += 1
                self.metrics['failed'] += 1
                self._log_audit('dlq', task)
            else:
                task.status = 'pending'

    def shutdown(self, timeout=None):
        with self._lock:
            self._accepting = False
        start = time.time()
        while True:
            with self._lock:
                running = [t for t in self.tasks if t.status == 'running']
            if not running:
                break
            if timeout and time.time() - start > timeout:
                break
            time.sleep(0.01)

    def snapshot(self, filepath):
        state = {
            'tasks': self.tasks,
            'dlq': self.dlq,
            'metrics': self.metrics,
        }
        data = pickle.dumps(state)
        enc = _xor_encrypt(data, self.key)
        with open(filepath, 'wb') as f:
            f.write(enc)

    @classmethod
    def restore(cls, filepath, data_dir='.', encryption_key=b'secret'):
        with open(filepath, 'rb') as f:
            enc = f.read()
        data = _xor_decrypt(enc, encryption_key)
        state = pickle.loads(data)
        q = cls(data_dir=data_dir, encryption_key=encryption_key)
        q.tasks = state['tasks']
        q.dlq = state['dlq']
        q.metrics = state['metrics']
        return q

    def get_metrics(self):
        lines = []
        lines.append(f'task_processed_total {self.metrics["processed"]}')
        lines.append(f'task_failed_total {self.metrics["failed"]}')
        lines.append(f'task_retries_total {self.metrics["retries"]}')
        lines.append(f'task_enqueued_total {self.metrics["enqueued"]}')
        lines.append(f'task_canceled_total {self.metrics["canceled"]}')
        lines.append(f'task_dlq_total {self.metrics["dlq"]}')
        return '\n'.join(lines)

    def get_stats(self):
        with self._lock:
            stats = {
                'pending': len([t for t in self.tasks if t.status == 'pending']),
                'running': len([t for t in self.tasks if t.status == 'running']),
                'finished': len([t for t in self.tasks if t.status == 'finished']),
                'dlq': len(self.dlq),
            }
        return stats

class WebDashboard:
    def __init__(self, queue: TaskQueue):
        self.queue = queue

    def render(self):
        stats = self.queue.get_stats()
        html = (f"<html><body>Pending: {stats['pending']}, "
                f"Running: {stats['running']}, "
                f"Finished: {stats['finished']}, "
                f"DLQ: {stats['dlq']}</body></html>")
        return html
