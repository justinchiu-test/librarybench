import bisect

def linear_interpolation(readings, timestamp):
    # Need at least two points to interpolate
    if len(readings) < 2:
        return None
    times = [ts for ts, _ in readings]
    # If timestamp is at or outside the bounds, or exactly matches an existing point, no interpolation
    if timestamp <= times[0] or timestamp >= times[-1] or timestamp in times:
        return None
    # Find the right-hand neighbor index
    idx = bisect.bisect_right(times, timestamp)
    t0, v0 = readings[idx - 1]
    t1, v1 = readings[idx]
    # Compute linear interpolation
    if isinstance(v0, dict):
        res = {}
        for k in v0.keys():
            res[k] = v0[k] + (v1[k] - v0[k]) * (timestamp - t0) / (t1 - t0)
        return res
    return v0 + (v1 - v0) * (timestamp - t0) / (t1 - t0)

def spline_interpolation(readings, timestamp):
    # For now, fallback to linear
    return linear_interpolation(readings, timestamp)
