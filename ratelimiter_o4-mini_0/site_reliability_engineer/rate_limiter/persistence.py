import json

def persist_bucket_state(policies, filepath):
    state = {}
    for name, p in policies.items():
        state[name] = p.get_metrics()
    with open(filepath, 'w') as f:
        json.dump(state, f)
    return True
