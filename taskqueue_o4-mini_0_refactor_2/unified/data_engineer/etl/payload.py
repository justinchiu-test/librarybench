import pickle

class BinaryPayloadSupport:
    def __init__(self):
        self.store = {}

    def store_payload(self, key, obj):
        self.store[key] = pickle.dumps(obj)

    def retrieve_payload(self, key):
        data = self.store.get(key)
        if data is None:
            return None
        return pickle.loads(data)
