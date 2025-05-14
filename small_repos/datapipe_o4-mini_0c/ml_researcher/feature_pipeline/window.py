def sliding_window(data, window_size, step):
    if window_size <= 0 or step <= 0:
        raise ValueError("window_size and step must be positive")
    windows = []
    for i in range(0, len(data) - window_size + 1, step):
        windows.append(data[i:i + window_size])
    return windows
