from plugin_ext.plugin import Plugin

def test_aggregated_error_reporting_with_custom_validator():
    plugin = Plugin()
    data = {'contact': 'bob@example.com'}
    # Run validator and report errors
    errs = plugin.gdpr_validator(data)
    for e in errs:
        plugin.report_error(e)
    assert len(plugin.errors) == len(errs)
    assert all(isinstance(e, dict) for e in plugin.errors)
