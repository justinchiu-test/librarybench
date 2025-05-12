"""
Abstract Persistence Backend Interface
"""
class PersistenceBackend:
    """Base class for persistence backends."""
    def __init__(self, *args, **kwargs):
        pass
    def load(self):  # pragma: no cover
        """Load stored data. Must be overridden."""
        raise NotImplementedError
    def save(self, data):  # pragma: no cover
        """Save provided data dict. Must be overridden."""
        raise NotImplementedError
    def load_job(self, job_id):
        """Load a single job entry by id."""
        data = self.load() or {}
        return data.get(job_id)
    def save_job(self, job_id, entry):
        """Save a single job entry by id."""
        data = self.load() or {}
        data[job_id] = entry
        self.save(data)