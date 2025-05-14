class FixedWindow:
    pass

class SlidingWindow:
    pass

class RollingWindow:
    pass

class TokenBucket:
    pass

class LeakyBucket:
    pass

def select_window_algo(name):
    name = name.lower()
    mapping = {
        "fixed": FixedWindow,
        "sliding": SlidingWindow,
        "rolling": RollingWindow,
        "token": TokenBucket,
        "leaky": LeakyBucket
    }
    if name not in mapping:
        raise ValueError(f"Unknown algorithm: {name}")
    return mapping[name]()
