import logging

class ContextLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        # Merge adapter.extra (the context) with kwargs passed in.
        merged = {}
        merged.update(self.extra or {})
        merged.update(kwargs or {})
        return msg, merged

def attach_log_context(logger, **context):
    """
    Returns an adapter whose process() merges your context dict
    with any kwargs you pass in.
    """
    return ContextLoggerAdapter(logger, context)
