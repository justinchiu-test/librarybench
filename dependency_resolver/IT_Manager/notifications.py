from manager import PackageManager

def get_update_notifications(pm):
    """
    pm: PackageManager
    Returns list of human-readable notifications.
    """
    updates = pm.check_updates()
    messages = []
    for name, (cur, new) in updates.items():
        messages.append(f"Package '{name}' can be updated from {cur} to {new}.")
    return messages
