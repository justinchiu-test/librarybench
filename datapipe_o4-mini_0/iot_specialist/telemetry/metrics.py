def export_prometheus_metrics(counters):
    """
    counters: dict of metric_name -> value
    returns text in Prometheus exposition format
    """
    lines = []
    for name, val in counters.items():
        lines.append(f"# TYPE {name} gauge")
        lines.append(f"{name} {val}")
    return "\n".join(lines)
