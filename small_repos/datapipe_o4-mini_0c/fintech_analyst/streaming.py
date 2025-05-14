import time

def run_streaming(source, process_func):
    for item in source:
        process_func(item)
        # simulate minimal latency
        time.sleep(0)
