import re
from datetime import datetime, timezone, timedelta

class TextField:
    def __init__(self, pattern=None, max_length=255, mask_sensitive=False):
        self.pattern = re.compile(pattern) if pattern else None
        self.max_length = max_length
        self.mask_sensitive = mask_sensitive
        self._raw_value = None

    def validate(self, value):
        if len(value) > self.max_length:
            return False, "Value exceeds maximum length"
        if self.pattern and not self.pattern.match(value):
            return False, "Value does not match required pattern"
        return True, None

    def input(self, value):
        valid, err = self.validate(value)
        if not valid:
            return False, err
        self._raw_value = value
        return True, None

    def get_value(self):
        if self.mask_sensitive and self._raw_value is not None:
            return "*" * len(self._raw_value)
        return self._raw_value

class DateTimePicker:
    def __init__(self, timezone_offset_hours=0):
        self.tz = timezone(timedelta(hours=timezone_offset_hours))
        self._picked = None

    def pick(self, dt):
        if not isinstance(dt, datetime):
            raise ValueError("Invalid datetime object")
        # Normalize to configured timezone
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        self._picked = dt.astimezone(self.tz)
        return self._picked

    def get_value(self):
        return self._picked
