import signal

def handle_signals(revoke_fn, logger):
    def handler(signum, frame):
        revoke_fn()
        logger.error("aborted for security")
        raise SystemExit(1)
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    return handler
