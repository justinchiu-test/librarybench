from pipeline.errors import skip_on_error

def run_batch(func, records):
    processed = succeeded = failed = 0
    print("Batch started")
    for record in records:
        processed += 1
        try:
            func(record)
            succeeded += 1
        except Exception:
            failed += 1
    print("Batch ended")
    return {'processed': processed, 'succeeded': succeeded, 'failed': failed}
