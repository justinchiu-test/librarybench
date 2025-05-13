from compliance.engine import ComplianceValidator
from compliance.plugins import CompliancePlugin

class DummyPlugin(CompliancePlugin):
    def __init__(self):
        self.before_called = False
        self.after_called = False

    def before_validate(self, request):
        self.before_called = True
        request["plugin_before"] = True

    def after_validate(self, result):
        self.after_called = True
        result["plugin_after"] = True

def test_plugin_hooks():
    plugin = DummyPlugin()
    validator = ComplianceValidator(strict_mode=True, plugins=[plugin])
    req = {
        "user_id": "u7",
        "age": 22,
        "data_retention_policy": "short_term",
        "user_consent_status": "granted",
    }
    res = validator.validate(req)
    assert plugin.before_called
    assert plugin.after_called
    assert res.get("plugin_before") is True
    assert res.get("plugin_after") is True
