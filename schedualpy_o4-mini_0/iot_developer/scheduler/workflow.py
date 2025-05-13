import time

class Workflow:
    def __init__(self):
        self._steps = []

    def add_step(self, func, retry_on_exception=(), max_retries=0):
        self._steps.append({
            'func': func,
            'retry_on': retry_on_exception,
            'max_retries': max_retries
        })
        return self

    def run(self, initial_input):
        data = initial_input
        for step in self._steps:
            attempts = 0
            while True:
                try:
                    data = step['func'](data)
                    break
                except step['retry_on'] as e:
                    attempts += 1
                    if attempts > step['max_retries']:
                        raise
                    time.sleep(0)  # yield
                except Exception:
                    raise
        return data
