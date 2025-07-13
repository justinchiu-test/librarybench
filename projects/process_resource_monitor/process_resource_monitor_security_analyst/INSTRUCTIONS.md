# Process Resource Monitor - Security Operations Analyst Edition

## Overview
You are building a Python-based process resource monitoring library specifically designed for Sarah, a SOC analyst monitoring for suspicious process behavior. The library should detect potential security threats through resource anomalies and identify cryptominers, data exfiltration, and other malicious activities through behavioral analysis.

## Core Requirements

### 1. Baseline Behavior Learning with Deviation Detection
- Implement machine learning algorithms to establish normal behavior baselines
- Create per-process profiles tracking typical CPU, memory, network, and disk patterns
- Detect statistical deviations from baseline using configurable sensitivity thresholds
- Support both supervised and unsupervised anomaly detection methods
- Maintain rolling baselines that adapt to legitimate changes over time

### 2. Cryptomining Detection through CPU/GPU Usage Patterns
- Identify processes with sustained high CPU/GPU usage characteristic of mining
- Detect mining pool communication patterns in network traffic
- Recognize common mining software signatures in process names and arguments
- Track unusual GPU access from typically CPU-only processes
- Correlate high resource usage with known mining algorithms and difficulty changes

### 3. Data Exfiltration Identification via Network I/O Spikes
- Monitor outbound network traffic volumes and detect unusual spikes
- Track data transfer ratios (upload vs download) for anomalies
- Identify connections to suspicious IP addresses or domains
- Detect slow, persistent data leaks designed to avoid detection
- Correlate file access patterns with subsequent network transfers

### 4. Process Launch Chain Analysis for Malware Detection
- Build process genealogy trees tracking parent-child relationships
- Identify suspicious process chains (e.g., Office → PowerShell → Network)
- Detect process hollowing and injection techniques
- Monitor for legitimate process impersonation
- Track lateral movement patterns across systems

### 5. SIEM Integration for Security Event Correlation
- Export security events in CEF, LEEF, or JSON formats
- Support real-time event streaming to popular SIEM platforms
- Implement severity scoring for automated alert prioritization
- Include contextual data for effective threat hunting
- Provide RESTful API for SIEM polling and webhook notifications

## Technical Specifications

### Data Collection
- High-frequency sampling (1-5 second intervals) for security-critical metrics
- Capture process command lines, environment variables, and file descriptors
- Monitor network connections with full socket details
- Track file system access patterns and registry modifications (where applicable)
- Implement tamper detection for monitoring components

### API Design
```python
# Example usage
monitor = SecurityResourceMonitor()

# Configure baseline learning
monitor.train_baseline(
    duration_hours=168,  # 1 week
    exclude_processes=["backup.exe", "antivirus.exe"]
)

# Enable threat detection
monitor.enable_detection(
    cryptomining=True,
    exfiltration=True,
    process_injection=True,
    sensitivity="high"
)

# Check for anomalies
threats = monitor.get_threats(
    severity_threshold="medium",
    time_window="1h"
)

# Generate SIEM event
for threat in threats:
    event = monitor.format_siem_event(
        threat,
        format="CEF",
        include_context=True
    )
    monitor.send_to_siem(event)
```

### Testing Requirements
- Comprehensive unit tests with >85% code coverage
- Integration tests with simulated attack scenarios
- False positive rate testing with normal workload variations
- Performance impact tests ensuring <5% overhead
- Use pytest with pytest-json-report for test result formatting
- Include test cases for common malware behaviors

### Performance Targets
- Detect cryptomining activity within 30 seconds of start
- Identify data exfiltration with <1% false positive rate
- Process 10,000 events per second for SIEM integration
- Maintain 30 days of detailed event history
- Generate threat reports in under 2 seconds

## Implementation Constraints
- Python 3.8+ compatibility required
- Use only Python standard library plus: psutil, scikit-learn, numpy, requests
- No GUI components - this is a backend library only
- All user interaction through Python API or CLI commands
- Minimize performance impact on monitored systems (<5% CPU overhead)

## Deliverables
1. Core Python library with all five security monitoring features
2. Machine learning models for baseline behavior detection
3. Comprehensive test suite including attack simulation tests
4. CLI tool for threat hunting and investigation
5. SIEM integration examples for Splunk, QRadar, and Elasticsearch