class BatchValidationInterface:
    def validate_batch(self, items):
        results = []
        success = 0
        fail = 0
        for item in items:
            r = self.validate_single(item)
            if r.get('valid'):
                success += 1
            else:
                fail += 1
            results.append(r)
        return {'results': results, 'success': success, 'fail': fail}
