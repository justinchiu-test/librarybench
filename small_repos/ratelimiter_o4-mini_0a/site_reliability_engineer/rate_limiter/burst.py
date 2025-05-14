def override_burst_capacity(policy, new_capacity):
    if hasattr(policy, "capacity"):
        policy.capacity = new_capacity
        return True
    raise ValueError("Cannot override burst capacity on this policy")
