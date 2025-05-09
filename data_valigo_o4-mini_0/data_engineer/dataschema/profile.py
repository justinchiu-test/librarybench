class ProfileRuleSet:
    def __init__(self):
        # {profile: {rule_name: rule_callable}}
        self._profiles = {}

    def add_rule(self, profile: str, name: str, rule):
        self._profiles.setdefault(profile, {})[name] = rule

    def get_rules(self, profile: str):
        return self._profiles.get(profile, {}).copy()

    def validate(self, profile: str, data):
        rules = self.get_rules(profile)
        results = {}
        for name, rule in rules.items():
            results[name] = rule(data)
        return results
