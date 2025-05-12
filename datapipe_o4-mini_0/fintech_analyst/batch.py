import logging

def run_batch(trades, process_func):
    logging.info("Batch processing started")
    results = []
    for t in trades:
        results.append(process_func(t))
    logging.info("Batch processing completed")
    return results
