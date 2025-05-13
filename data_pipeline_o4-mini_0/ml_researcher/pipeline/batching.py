class BuiltInBatch:
    def __init__(self, size=None, time_window=None):
        if size is None and time_window is None:
            raise ValueError("Must specify size or time_window")
        self.size = size
        self.time_window = time_window

    def batch(self, records):
        batches = []
        # size-based batching
        if self.size:
            for i in range(0, len(records), self.size):
                batches.append(records[i : i + self.size])
            return batches
        # time-based batching
        import datetime
        current_batch = []
        start_time = None
        for rec in records:
            ts = rec.get("timestamp")
            if not isinstance(ts, datetime.datetime):
                raise ValueError("Record missing datetime timestamp")
            if start_time is None:
                start_time = ts
                current_batch = [rec]
            else:
                delta = (ts - start_time).total_seconds()
                if delta <= self.time_window:
                    current_batch.append(rec)
                else:
                    batches.append(current_batch)
                    start_time = ts
                    current_batch = [rec]
        if current_batch:
            batches.append(current_batch)
        return batches
