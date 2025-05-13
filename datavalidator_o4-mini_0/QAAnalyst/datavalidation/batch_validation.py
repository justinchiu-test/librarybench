class BatchValidationInterface:
    def __init__(self, single_validator):
        self.validator = single_validator

    def validate_batch(self, records):
        results = []
        for record in records:
            res = self.validator.validate_single(record)
            results.append(res)
        total = len(results)
        failed = sum(1 for r in results if not r['valid'])
        return {'total': total, 'failed': failed, 'details': results}
