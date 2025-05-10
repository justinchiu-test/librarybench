import hashlib

class SecureFieldMasking:
    def __init__(self, fields, mask='****', hash_fields=None):
        self.fields = set(fields)
        self.mask = mask
        self.hash_fields = set(hash_fields or [])

    def mask_data(self, data: dict) -> dict:
        result = data.copy()
        for field in self.fields:
            if field in result:
                if field in self.hash_fields:
                    result[field] = hashlib.sha256(str(result[field]).encode()).hexdigest()
                else:
                    result[field] = self.mask
        return result
