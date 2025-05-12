from enum import Enum
from datetime import datetime, timedelta
import re

class Optimizer(Enum):
    SGD = 'sgd'
    ADAM = 'adam'

def coerce_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d')

def coerce_duration(duration_str):
    match = re.match(r'(\d+)(min|h)', duration_str)
    if not match:
        raise ValueError(f"Invalid duration: {duration_str}")
    val, unit = match.groups()
    val = int(val)
    if unit == 'min':
        return timedelta(minutes=val)
    else:
        return timedelta(hours=val)

def coerce_optimizer(opt_str):
    try:
        return Optimizer(opt_str.lower())
    except ValueError:
        raise ValueError(f"Unknown optimizer: {opt_str}")
