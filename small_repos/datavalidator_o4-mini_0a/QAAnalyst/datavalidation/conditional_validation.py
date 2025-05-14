class ConditionalValidation:
    def __init__(self):
        self.conditions = {}

    def add_condition(self, name, func):
        self.conditions[name] = func

    def validate(self, record, scenario):
        func = self.conditions.get(scenario)
        if not func:
            return []
        return func(record)
