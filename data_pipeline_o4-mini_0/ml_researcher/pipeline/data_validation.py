class DataValidation:
    def __init__(self, rules=None, schema=None):
        self.rules = rules or {}
        self.schema = schema or {}

    def validate(self, records):
        valid = []
        invalid = []
        for rec in records:
            ok = True
            # apply rules
            for field, rule in self.rules.items():
                if field in rec:
                    try:
                        if not rule(rec[field]):
                            ok = False
                    except Exception:
                        ok = False
                else:
                    ok = False
            # apply schema types
            for field, typ in self.schema.items():
                if field in rec:
                    if not isinstance(rec[field], typ):
                        ok = False
                else:
                    ok = False
            if ok:
                valid.append(rec)
            else:
                invalid.append(rec)
        return valid, invalid
