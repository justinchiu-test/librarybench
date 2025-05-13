class ErrorCodeSupport:
    def __init__(self):
        self.codes = {
            'missing_field': 100,
            'length_exceeded': 200,
            'optional_missing': 300,
            'conditional_failed': 400,
        }

    def get_error_code(self, rule):
        return self.codes.get(rule, -1)
