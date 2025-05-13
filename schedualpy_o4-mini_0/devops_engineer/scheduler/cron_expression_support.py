import re

class CronExpressionSupport:
    CRON_REGEX = re.compile(r'^(\S+\s+){4,5}\S+$')

    @staticmethod
    def validate(expr):
        if not CronExpressionSupport.CRON_REGEX.match(expr.strip()):
            raise ValueError("Invalid cron expression")
        parts = expr.strip().split()
        if len(parts) not in (5, 6):
            raise ValueError("Cron expression must have 5 or 6 fields")
        return True
