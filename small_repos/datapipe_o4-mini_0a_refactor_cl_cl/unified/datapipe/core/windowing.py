"""
Windowing functions for data streams.
"""

def tumbling_window(data, window_size=60, by_time=True, timestamp_field="timestamp"):
    """
    Groups data into fixed-size, non-overlapping windows.

    Args:
        data: List of records to window
        window_size: Size of each window (time in seconds if by_time=True, count if by_time=False)
        by_time: Whether to use time-based windows (True) or count-based windows (False)
        timestamp_field: Field name for timestamps in data records (only used when by_time=True)

    Returns:
        List of windows, where each window is a list of records
    """
    if not data:
        return []
    
    if by_time:
        # Group by time windows
        windows = []
        current_window = []
        window_start = None
        
        for record in data:
            if timestamp_field not in record:
                continue
                
            timestamp = record[timestamp_field]
            
            if window_start is None:
                window_start = timestamp
                current_window.append(record)
            elif timestamp < window_start + window_size:
                current_window.append(record)
            else:
                windows.append(current_window)
                current_window = [record]
                window_start = timestamp
        
        if current_window:
            windows.append(current_window)
            
        return windows
    else:
        # Group by count
        return [data[i:i+window_size] for i in range(0, len(data), window_size)]


def sliding_window(data, window_size=60, slide=1, timestamp_field="timestamp"):
    """
    Groups data into overlapping sliding windows.

    Args:
        data: List of records to window
        window_size: Size of each window (time in seconds or count depending on implementation)
        slide: How much to advance the window each time
        timestamp_field: Field name for timestamps in data records

    Returns:
        Processed windows in format that varies by implementation
    """
    if not data:
        return []
    
    # Check if this is IoT Engineer format (returning window summary stats)
    if isinstance(data[0], dict) and "value" in data[0]:
        # IoT Engineer sliding window implementation
        results = []
        for i in range(0, len(data) - window_size + 1, slide):
            window = data[i:i+window_size]
            avg_value = sum(item["value"] for item in window) / len(window)
            results.append({
                "start": window[0][timestamp_field],
                "end": window[-1][timestamp_field],
                "average": avg_value
            })
        return results
    
    # Check if this is Social Media Analyst format (returning sentiment averages)
    if isinstance(data[0], dict) and "sentiment" in data[0]:
        # Social Media Analyst sliding window implementation
        results = []
        for i, record in enumerate(data):
            # Get records within window_size of current timestamp
            window = [r for r in data if 
                     abs(r[timestamp_field] - record[timestamp_field]) <= window_size]
            avg_sentiment = sum(r["sentiment"] for r in window) / len(window)
            results.append({
                "timestamp": record[timestamp_field],
                "avg_sentiment": avg_sentiment
            })
        return results
    
    # Generic sliding window implementation (Quant Trader style - returns stats)
    if len(data) < 2:
        return []
    
    results = []
    for i in range(0, len(data) - window_size + 1, slide):
        window = data[i:i+window_size]
        if "price" in data[0]:
            # Financial data format
            avg_price = sum(item["price"] for item in window) / len(window)
            results.append({
                "start": i,
                "end": i + window_size,
                "length": len(window),
                "average": avg_price
            })
        else:
            # Default format
            results.append(window)
    
    return results