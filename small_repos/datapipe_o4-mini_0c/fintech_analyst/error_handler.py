import logging

def skip_on_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error("Error processing record: %s", e)
            return None
    return wrapper
