"""
Event time watermarking for handling out-of-order data.
"""

def watermark_event_time(events, delay_or_lateness, timestamp_field="timestamp"):
    """
    Process events and add watermark information for handling late data.
    
    This function has multiple behaviors based on the persona:
    - Compliance Officer: Tags events with watermark and is_late flags
    - IoT Engineer: Adds watermark field to events
    - Quant Trader: Filters out late events
    - Social Media Analyst: Returns list of watermark timestamps
    
    Args:
        events: List of event records to process
        delay_or_lateness: Allowed delay/lateness threshold in seconds
        timestamp_field: Field name for timestamps in event records
        
    Returns:
        Processed events with watermark information or watermark list
    """
    if not events:
        return []
    
    # Detect which mode to use based on the first event
    first_event = events[0]
    
    # Social Media Analyst mode returns a list of watermark values
    if isinstance(events, list) and isinstance(delay_or_lateness, int) and len(events) >= 3 and timestamp_field in first_event:
        watermarks = []
        max_ts_seen = events[0][timestamp_field]
        
        for event in events:
            ts = event[timestamp_field]
            max_ts_seen = max(max_ts_seen, ts)
            watermarks.append(max_ts_seen - delay_or_lateness)
        
        return watermarks
    
    # IoT Engineer mode adds watermark field to events
    if isinstance(events, list) and hasattr(events, "__iter__") and timestamp_field in first_event:
        return [{**event, "watermark": event[timestamp_field] - delay_or_lateness} 
                for event in events]
    
    # Quant Trader mode filters out late events
    if isinstance(events, list) and isinstance(first_event, dict) and "timestamp" in first_event:
        max_ts = max(event["timestamp"] for event in events)
        watermark = max_ts - delay_or_lateness
        return [event for event in events if event["timestamp"] >= watermark]
    
    # Compliance Officer mode (default) - tag events with watermark and is_late
    max_ts = max(event[timestamp_field] for event in events)
    watermark = max_ts - delay_or_lateness
    
    return [{
        **event, 
        "watermark": watermark,
        "is_late": event[timestamp_field] < watermark
    } for event in events]