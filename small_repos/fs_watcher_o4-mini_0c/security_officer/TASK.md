# The Task

I am a security analyst monitoring file integrity on critical servers. I want to detect unauthorized changes, unauthorized moves, or hidden/temp file drops. This code repository powers my intrusion-detection hooks and audit reports.

# The Requirements

* `start_metrics_endpoint` : report event rates, anomaly counts, and latency into our SIEM via HTTP callbacks  
* `scan_once`              : perform periodic full scans to compare baselines and flag unexpected changes  
* `register_plugin`        : add custom filters for known‐safe patch files, transformation plugins for checksumming, and sinks to our alerting service  
* `set_thread_pool_size`   : manage concurrency of deep‐content scans without overloading I/O  
* `configure_logging`      : log at warning/error for suspicious activity, info for routine scans  
* `set_handler_timeout`    : abort prolonged content‐hashing tasks that could indicate tampering loops  
* `set_throttle_rate`      : throttle flood of events during patched‐file rollouts  
* `generate_change_summary`: daily audit report (“20 files changed, 2 moved, 3 deleted”) for compliance  
* `enable_move_detection`  : correlate delete+create to detect stealthy renames by attackers  
* `add_ignore_rule`        : exclude OS swap files and predefined benign temporary files
