class ConflictReporting:
    @staticmethod
    def find_conflicts(*dicts):
        values = {}
        conflicts = {}
        for d in dicts:
            for k, v in d.items():
                if k not in values:
                    values[k] = set([v])
                else:
                    values[k].add(v)
        for k, vs in values.items():
            if len(vs) > 1:
                conflicts[k] = vs
        return conflicts
