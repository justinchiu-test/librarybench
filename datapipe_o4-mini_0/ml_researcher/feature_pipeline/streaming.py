from .schema import validate_schema

def run_streaming(event_source, process_func, schema=None, serializer=None, metrics=None):
    results = []
    for event in event_source:
        try:
            if schema:
                validate_schema(event, schema)
            processed = process_func(event)
            if serializer:
                fmt = processed.get('format')
                data = processed.get('data')
                serialized = serializer.serialize(fmt, data)
            else:
                serialized = processed
            if metrics:
                metrics.inc('records_processed')
            results.append(serialized)
        except Exception:
            if metrics:
                metrics.inc('records_failed')
            continue
    return results
