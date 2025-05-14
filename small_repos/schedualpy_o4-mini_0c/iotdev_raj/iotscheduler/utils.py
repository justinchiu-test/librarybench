import random
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# Subclass ZoneInfo to provide a .zone attribute for compatibility with tests
class _ZoneInfoWithZone(ZoneInfo):
    @property
    def zone(self):
        return self.key

# Plugin registry
_PLUGIN_REGISTRY = {}

def enable_daylight_saving_support(dt: datetime, tz_str: str) -> datetime:
    """
    Adjust a naive or UTC datetime to the specified timezone, accounting for DST.
    """
    tz = _ZoneInfoWithZone(tz_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz)

def apply_jitter_and_drift_correction(base_interval: float, jitter: float, drift: float) -> float:
    """
    Add random jitter and subtract drift from base_interval.
    jitter: max seconds to add or subtract
    drift: seconds to subtract
    """
    offset = random.uniform(-jitter, jitter)
    return base_interval + offset - drift

def load_plugin(plugin_name: str):
    """
    Load a plugin by name from the registry.
    """
    return _PLUGIN_REGISTRY.get(plugin_name)

def register_plugin(plugin_name: str, plugin_cls):
    """
    Register a plugin class under a name.
    """
    _PLUGIN_REGISTRY[plugin_name] = plugin_cls

def create_task_group(name: str, devices: list) -> dict:
    """
    Create a group mapping for devices.
    """
    return {"group_name": name, "devices": list(devices)}
