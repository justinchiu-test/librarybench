import re
from datetime import datetime

class TextField:
    def __init__(self, name, regex=None, max_length=None, placeholder=''):
        self.name = name
        self.regex = re.compile(regex) if regex else None
        self.max_length = max_length
        self.placeholder = placeholder

    def validate(self, value):
        if self.max_length is not None and len(value) > self.max_length:
            raise ValueError(f"Value for {self.name} exceeds max length {self.max_length}")
        if self.regex and not self.regex.match(value):
            raise ValueError(f"Value for {self.name} does not match pattern")
        return True

class DateTimePicker:
    def __init__(self):
        self.selected_date = None
        self.selected_time = None

    def pick_date(self, date_str):
        try:
            self.selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            return self.selected_date
        except ValueError:
            raise ValueError("Invalid date format, expected YYYY-MM-DD")

    def pick_time(self, time_str):
        try:
            self.selected_time = datetime.strptime(time_str, "%H:%M").time()
            return self.selected_time
        except ValueError:
            raise ValueError("Invalid time format, expected HH:MM")
