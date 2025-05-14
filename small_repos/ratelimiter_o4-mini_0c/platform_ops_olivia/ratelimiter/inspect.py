def inspect_limiter(limiter):
    state = {}
    if hasattr(limiter, 'capacity'):
        state['capacity'] = limiter.capacity
    if hasattr(limiter, 'tokens'):
        state['tokens'] = limiter.tokens
    return state
