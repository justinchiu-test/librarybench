import pytest
from ComplianceOfficer.compliance_repo.store import ComplianceStore

def test_custom_plugin_called():
    cs = ComplianceStore()
    calls = []
    def plugin(ev):
        calls.append(ev)
    cs.registerPlugin(plugin)
    cs.updateDocument('pp', {'f':1})
    assert calls and calls[0]['type']=='update'
