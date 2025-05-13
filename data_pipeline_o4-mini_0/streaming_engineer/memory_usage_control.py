import os

class MemoryUsageControl:
    def __init__(self, threshold_bytes, spill_file_path):
        self.threshold = threshold_bytes
        self.spill_file_path = spill_file_path

    def check_and_spill(self, current_usage_bytes, data):
        # Spill when usage is at or above threshold
        if current_usage_bytes >= self.threshold:
            # Ensure directory exists
            dirpath = os.path.dirname(self.spill_file_path)
            if dirpath and not os.path.exists(dirpath):
                os.makedirs(dirpath, exist_ok=True)
            # Spill to disk
            with open(self.spill_file_path, 'a') as f:
                for item in data:
                    f.write(str(item) + '\n')
            return []
        return data
