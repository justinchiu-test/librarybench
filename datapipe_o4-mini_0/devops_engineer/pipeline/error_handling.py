import logging
logger = logging.getLogger(__name__)

def skip_on_error(func):
    def wrapper(record, *args, **kwargs):
        try:
            return func(record, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error processing record {record}: {e}")
            return None
    return wrapper
