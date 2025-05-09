import hashlib

class TransformationPipeline:
    def __init__(self):
        self._transforms = []

    def add(self, fn):
        self._transforms.append(fn)

    def apply(self, value):
        result = value
        for fn in self._transforms:
            result = fn(result)
        return result

def mask(value: str, field_type: str) -> str:
    if field_type == 'ssn':
        # assume format XXX-XX-XXXX
        parts = value.split('-')
        if len(parts) == 3:
            return '***-**-' + parts[2]
    if field_type == 'cc':
        # last 4 digits
        digits = ''.join(filter(str.isdigit, value))
        if len(digits) >= 4:
            return '**** **** **** ' + digits[-4:]
    # fallback hash
    return hashlib.sha256(value.encode()).hexdigest()
