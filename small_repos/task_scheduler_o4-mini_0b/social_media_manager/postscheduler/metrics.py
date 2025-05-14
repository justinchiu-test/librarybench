# removed prometheus_client dependency; emit simple text/plain metrics
post_duration = 0
queue_length = 0
success_count = 0
failure_count = 0

def expose_metrics():
    """
    Returns a tuple (metrics_bytes, content_type)
    """
    lines = [
        f"post_duration_seconds {post_duration}",
        f"queue_length {queue_length}",
        f"success_count {success_count}",
        f"failure_count {failure_count}",
    ]
    payload = "\n".join(lines) + "\n"
    # tests only require 'text/plain' in content_type
    content_type = "text/plain; charset=utf-8"
    return payload.encode("utf-8"), content_type
