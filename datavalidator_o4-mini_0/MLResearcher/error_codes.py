class ErrorCodeSupport:
    MISSING_FEATURE = "MISSING_FEATURE"
    OUTLIER_DETECTED = "OUTLIER_DETECTED"
    INVALID_LENGTH = "INVALID_LENGTH"
    INVALID_VALUE = "INVALID_VALUE"

    def assign_error_codes(self, errors):
        codes = []
        for e in errors:
            et = e.get('type')
            if et == 'missing':
                codes.append(self.MISSING_FEATURE)
            elif et == 'outlier':
                codes.append(self.OUTLIER_DETECTED)
            elif et == 'length':
                codes.append(self.INVALID_LENGTH)
            else:
                codes.append(self.INVALID_VALUE)
        return codes
