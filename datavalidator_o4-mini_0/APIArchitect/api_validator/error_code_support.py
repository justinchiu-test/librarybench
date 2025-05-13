class ErrorCodeSupport:
    @staticmethod
    def assign_code(field, error_type):
        return f"{field.upper()}_{error_type.upper()}"
