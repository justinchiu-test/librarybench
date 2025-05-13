class DataValidator:
    def __init__(self, required_fields):
        self.required = required_fields
    def validate(self, data):
        for field in self.required:
            if field not in data:
                raise ValueError(f"Missing field: {field}")
        return True

class SchemaEnforcer:
    @staticmethod
    def enforce(read):
        if not all(k in read for k in ('id', 'seq', 'quality')):
            raise ValueError("Invalid FASTQ read format")
        if any(c not in 'ACGTN' for c in read['seq']):
            raise ValueError("Invalid nucleotide in sequence")
        return True
