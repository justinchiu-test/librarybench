def run_batch(data, processor, notifier=None):
    results = []
    for item in data:
        results.append(processor(item))
    if notifier:
        notifier(len(results), results)
    return results
