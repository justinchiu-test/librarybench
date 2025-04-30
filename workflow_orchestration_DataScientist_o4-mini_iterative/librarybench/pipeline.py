import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

from .metadata import MetadataRecord
from .task import Task

class Pipeline:
    def __init__(self, tasks, context, metadata, notifier):
        # tasks: list of Task
        self._initial = list(tasks)
        self.context = context
        self.metadata = metadata
        self.notifier = notifier

    def run(self):
        queue = deque(self._initial)

        while queue:
            task = queue.popleft()
            # set up retry variables
            max_retries = task.max_retries or 0
            base_delay = task.retry_delay_seconds or 0
            delay = base_delay

            succeeded = False
            # Perform attempts: 1 initial + max_retries
            for attempt in range(1, max_retries + 2):
                task.attempts = attempt
                start = time.time()

                try:
                    # Execute with timeout if given
                    if task.timeout is not None:
                        with ThreadPoolExecutor(max_workers=1) as executor:
                            future = executor.submit(task.func, self.context)
                            result = future.result(timeout=task.timeout)
                    else:
                        result = task.func(self.context)
                    end = time.time()

                    # SUCCESS path
                    # 1) dynamic tasks
                    if isinstance(result, list) and all(isinstance(t, Task) for t in result):
                        task.state = 'success'
                        rec = MetadataRecord(task.name, attempt, task.state, start, end)
                        self.metadata.add(rec)
                        # prepend new tasks in original order
                        for new in result:
                            queue.appendleft(new)
                    else:
                        # 2) normal output dict
                        if isinstance(result, dict):
                            for k, v in result.items():
                                self.context.set(k, v)
                        task.state = 'success'
                        rec = MetadataRecord(task.name, attempt, task.state, start, end)
                        self.metadata.add(rec)

                    succeeded = True
                    break

                except FutureTimeoutError as to_err:
                    error = to_err
                    status = 'failure'
                    end = time.time()
                except Exception as ex:
                    error = ex
                    status = 'failure'
                    end = time.time()

                # record this failed attempt
                rec = MetadataRecord(task.name, attempt, status, start, end, error)
                self.metadata.add(rec)

                # if more retries remain, sleep and potentially back‐off
                if attempt <= max_retries:
                    time.sleep(delay)
                    if task.backoff:
                        delay *= 2
                else:
                    # final failure
                    task.state = 'failure'
                    # send alert
                    self.notifier.notify(f"Task {task.name} failed: {error}")

            # end for attempts
        # end while queue
