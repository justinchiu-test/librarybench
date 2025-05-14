def run_streaming(generator, func, max_events=None):
    processed = succeeded = failed = 0
    for event in generator:
        if max_events is not None and processed >= max_events:
            break
        processed += 1
        try:
            func(event)
            succeeded += 1
        except Exception:
            failed += 1
    return {'processed': processed, 'succeeded': succeeded, 'failed': failed}
