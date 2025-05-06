from manager import PackageManager

def get_update_notifications(pm):
    """
    pm: PackageManager
    Returns list of human-readable notifications.
    """
    updates = pm.check_updates()
    return [f"Package '{n}' can be updated from {c} to {u}."
            for n, (c, u) in updates.items()]
