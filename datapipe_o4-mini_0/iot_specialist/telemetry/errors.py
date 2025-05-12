failed_devices = []

def skip_on_error(device_id, reading, min_val=None, max_val=None):
    try:
        if reading is None:
            raise ValueError("Missing reading")
        if min_val is not None and reading < min_val:
            raise ValueError("Below minimum")
        if max_val is not None and reading > max_val:
            raise ValueError("Above maximum")
        return True
    except Exception:
        failed_devices.append(device_id)
        return False
