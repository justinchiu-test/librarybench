import hashlib

class SecureFieldMasking:
    @staticmethod
    def redact(value):
        return '****'

    @staticmethod
    def hash(value):
        if not isinstance(value, str):
            value = str(value)
        return hashlib.sha256(value.encode('utf-8')).hexdigest()
