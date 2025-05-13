_handlers = []

def register_error_handler(fn):
    """
    fn: callable that takes one argument (error)
    """
    _handlers.append(fn)

def trigger_error(error):
    """
    Calls all registered handlers with the error
    """
    for fn in _handlers:
        fn(error)
