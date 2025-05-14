from . import config

def scaffold_pipeline(name):
    # Stub implementation: return scaffold path message
    return f"Scaffolded pipeline at {name}"

def run_pipeline(name, processor=None, records=None):
    mode = 'streaming' if config.streaming else 'batch'
    return f"Running pipeline {name} in {mode} mode"

def monitor_pipeline(name):
    return f"Monitoring pipeline {name}"

def debug_pipeline(name):
    return f"Debugging pipeline {name}"

def enable_streaming():
    config.streaming = True

def set_skip_on_error():
    config.skip_on_error = True
