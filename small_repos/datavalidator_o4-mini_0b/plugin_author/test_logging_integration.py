import logging
from plugin_ext.plugin import Plugin

def test_logging_integration_namespace():
    plugin = Plugin()
    # Capture logs
    records = []
    handler = logging.Handler()
    def emit(record):
        records.append(record)
    handler.emit = emit
    logger = logging.getLogger('plugin_ext')
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    # Emit log
    plugin.logger.info("Test message")
    assert len(records) == 1
    assert records[0].msg == "Test message"
    logger.removeHandler(handler)
