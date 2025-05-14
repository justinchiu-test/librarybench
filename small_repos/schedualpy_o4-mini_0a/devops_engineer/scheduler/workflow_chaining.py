class WorkflowChain:
    def __init__(self):
        self._tasks = []

    def add_task(self, func, on_success=None, on_failure=None):
        if not callable(func):
            raise ValueError("Task must be callable")
        self._tasks.append((func, on_success, on_failure))

    def run_chain(self, initial_value=None):
        result = initial_value
        for func, on_success, on_failure in self._tasks:
            try:
                result = func(result)
                if on_success:
                    result = on_success(result)
            except Exception as e:
                if on_failure:
                    result = on_failure(e)
                    continue
                else:
                    raise
        return result
