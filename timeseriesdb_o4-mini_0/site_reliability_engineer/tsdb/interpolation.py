import bisect

class Interpolation:
    @staticmethod
    def linear(points, start, end, interval):
        # points: list of (ts, val)
        if not points:
            return []
        points = sorted(points, key=lambda x: x[0])
        ts_list = [ts for ts, _ in points]
        val_list = [v for _, v in points]
        result = []
        t = start
        while t <= end:
            # if exact
            if t in ts_list:
                v = val_list[ts_list.index(t)]
            else:
                # find surrounding
                idx = bisect.bisect_left(ts_list, t)
                if idx == 0 or idx >= len(ts_list):
                    v = None
                else:
                    t0, v0 = points[idx-1]
                    t1, v1 = points[idx]
                    ratio = (t - t0) / (t1 - t0)
                    v = v0 + ratio * (v1 - v0)
            result.append((t, v))
            t += interval
        return result

    @staticmethod
    def step(points, start, end, interval):
        if not points:
            return []
        points = sorted(points, key=lambda x: x[0])
        ts_list = [ts for ts, _ in points]
        val_list = [v for _, v in points]
        result = []
        t = start
        last = None
        while t <= end:
            # find last known <= t
            idx = bisect.bisect_right(ts_list, t) - 1
            if idx >= 0:
                last = val_list[idx]
            result.append((t, last))
            t += interval
        return result
