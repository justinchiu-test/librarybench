class StopCondition:
    def __call__(self, attempts, last_exception):
        raise NotImplementedError
