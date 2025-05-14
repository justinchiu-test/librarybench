class DefaultValues:
    def set_default_values(self, record, defaults):
        new_record = dict(record)
        for key, val in defaults.items():
            if key not in new_record or new_record[key] is None:
                new_record[key] = val
        return new_record
