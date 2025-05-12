def sliding_window_vwap(data, window_size):
    if window_size <= 0:
        raise ValueError("window_size must be positive")
    result = []
    for i in range(len(data) - window_size + 1):
        window = data[i:i+window_size]
        total_pv = sum(price * volume for price, volume in window)
        total_v = sum(volume for _, volume in window)
        if total_v == 0:
            result.append(0)
        else:
            result.append(total_pv / total_v)
    return result

def tumbling_candles(prices, window_size):
    if window_size <= 0:
        raise ValueError("window_size must be positive")
    candles = []
    for i in range(0, len(prices), window_size):
        chunk = prices[i:i+window_size]
        if not chunk:
            continue
        candles.append({
            'open': chunk[0],
            'high': max(chunk),
            'low': min(chunk),
            'close': chunk[-1],
        })
    return candles
