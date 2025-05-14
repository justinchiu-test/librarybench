import os

class EventHistoryStore:
    """
    Stores events into a rolling log, rotating when exceeding max_bytes.
    """
    def __init__(self, log_dir: str, max_bytes: int = 0, backup_count: int = 0):
        self.log_dir = log_dir
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.base_filename = "events.log"
        # ensure the log directory exists
        os.makedirs(self.log_dir, exist_ok=True)

    def write_event(self, event):
        # ensure dir exists
        os.makedirs(self.log_dir, exist_ok=True)
        base_path = os.path.join(self.log_dir, self.base_filename)
        # rotate if over size
        try:
            if os.path.exists(base_path) and os.path.getsize(base_path) >= self.max_bytes:
                self._rotate_files()
        except OSError:
            # if any issue checking or rotating, ignore and proceed
            pass

        # prepare CSV line: type,src,dest,is_dir
        line = f"{event.event_type},{event.src_path},{event.dest_path or ''},{int(event.is_directory)}\n"
        with open(base_path, "a", encoding="utf-8") as f:
            f.write(line)

    def _rotate_files(self):
        """
        Rotate log files:
          - Delete the oldest backup if it exists
          - Shift events.log.(i) -> events.log.(i+1)
          - Rename events.log -> events.log.1
        """
        # remove the oldest if at capacity
        if self.backup_count > 0:
            oldest = os.path.join(self.log_dir, f"{self.base_filename}.{self.backup_count}")
            if os.path.exists(oldest):
                os.remove(oldest)
            # shift existing backups
            for i in range(self.backup_count - 1, 0, -1):
                src = os.path.join(self.log_dir, f"{self.base_filename}.{i}")
                dst = os.path.join(self.log_dir, f"{self.base_filename}.{i+1}")
                if os.path.exists(src):
                    os.rename(src, dst)
            # shift the main log
            main_log = os.path.join(self.log_dir, self.base_filename)
            if os.path.exists(main_log):
                os.rename(main_log, os.path.join(self.log_dir, f"{self.base_filename}.1"))
        else:
            # no backups desired; simply remove the main log
            main_log = os.path.join(self.log_dir, self.base_filename)
            if os.path.exists(main_log):
                os.remove(main_log)
