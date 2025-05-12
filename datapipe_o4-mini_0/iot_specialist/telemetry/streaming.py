def run_streaming(source, process):
    """
    source: iterable of messages
    process: function(msg) -> result
    returns list of processed messages
    """
    results = []
    for msg in source:
        results.append(process(msg))
    return results
