from plugin_ext.plugin import Plugin

def test_report_error_appends_to_errors():
    plugin = Plugin()
    assert plugin.errors == []
    err = {'code': 'E001', 'message': 'Test error'}
    plugin.report_error(err)
    assert plugin.errors == [err]
