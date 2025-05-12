def windowed_operations(records, window_size, window_type='count', slide=None):
    windows = []
    if window_type == 'count':
        if slide is None:
            # Tumbling count windows
            for i in range(0, len(records), window_size):
                windows.append(records[i:i + window_size])
        else:
            # Sliding count windows, include partials at the end
            for i in range(0, len(records), slide):
                window = records[i:i + window_size]
                if window:
                    windows.append(window)
    else:
        # Time-based windows
        current = []
        start_time = None
        for rec in records:
            timestamp = rec[0]
            if start_time is None:
                start_time = timestamp
                current = [rec]
            elif timestamp - start_time < window_size:
                current.append(rec)
            else:
                windows.append(current)
                start_time = timestamp
                current = [rec]
        if current:
            windows.append(current)
    return windows
