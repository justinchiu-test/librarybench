import time

class SkipError(Exception):
    pass

class RetryError(Exception):
    pass

def error_handling_skip(fn):
    def wrapper(records):
        output = []
        for r in records:
            try:
                output.extend(fn([r]))
            except Exception:
                continue
        return output
    return wrapper

def error_handling_retry(max_retries=3, backoff=0.1):
    def decorator(fn):
        def wrapper(records):
            output = []
            for r in records:
                attempts = 0
                while True:
                    try:
                        result = fn([r])
                        output.extend(result)
                        break
                    except Exception:
                        attempts += 1
                        if attempts >= max_retries:
                            break
                        time.sleep(backoff)
                # skip if still failing
            return output
        return wrapper
    return decorator
