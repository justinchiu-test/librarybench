priority_map = {}

def assign_priority_bucket(key, priority):
    priority_map[key] = priority
    return True

def get_priority(key):
    return priority_map.get(key)
