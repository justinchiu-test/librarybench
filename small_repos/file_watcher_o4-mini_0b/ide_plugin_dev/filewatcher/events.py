import time
class Event:
    def __init__(self, event_type, src_path, dest_path=None, diff=None):
        self.event_type = event_type  # 'created','modified','deleted','moved'
        self.src_path = src_path
        self.dest_path = dest_path
        self.diff = diff
        self.timestamp = time.time()
    def to_dict(self):
        return {
            'event_type': self.event_type,
            'src_path': self.src_path,
            'dest_path': self.dest_path,
            'diff': self.diff,
            'timestamp': self.timestamp,
        }
    def __repr__(self):
        return f"<Event {self.event_type} {self.src_path} -> {self.dest_path if self.dest_path else ''}>"
