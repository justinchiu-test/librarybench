LOGS = []

def log_event(action, decision, metadata=None):
    entry = {
        "action": action,
        "decision": decision,
        "metadata": metadata or {}
    }
    LOGS.append(entry)
    return entry
