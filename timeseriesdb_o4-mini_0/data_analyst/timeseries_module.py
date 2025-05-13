import csv
import io
import datetime
from zoneinfo import ZoneInfo
import threading

_alerts = {}
_write_history = []
_compression_registry = {}
_cache_registry = {}
_cardinality_limits = {}
_cardinality_values = {}
_callbacks = {}
_callbacks_lock = threading.Lock()

def export_csv(series_list, start_time, end_time, tag_filters):
    """
    series_list: list of dicts with keys 'id', 'data', 'tags'
      'data' is list of (datetime, value)
      'tags' is dict of tag_key: tag_value
    start_time, end_time: datetime for filtering
    tag_filters: dict of tag_key: tag_value to filter series
    Returns CSV string with columns timestamp,series_id,value
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['timestamp', 'series_id', 'value'])
    rows = []
    for series in series_list:
        tags = series.get('tags', {})
        if all(tags.get(k) == v for k, v in tag_filters.items()):
            sid = series.get('id')
            for ts, val in series.get('data', []):
                if ts >= start_time and ts <= end_time:
                    rows.append((ts.isoformat(), sid, val))
    rows.sort(key=lambda x: (x[0], x[1]))
    for r in rows:
        writer.writerow(r)
    return output.getvalue()

def define_alert(alert_name, series_id, condition, severity, notify_channels):
    """
    Registers an alert with given parameters.
    """
    alert = {
        'name': alert_name,
        'series_id': series_id,
        'condition': condition,
        'severity': severity,
        'notify_channels': notify_channels
    }
    _alerts[alert_name] = alert
    return alert

def convert_timezone(query_params, local_timezone):
    """
    query_params: dict with 'start_time' and 'end_time' as datetime (UTC)
    local_timezone: tz string
    Returns new dict with times converted to local timezone
    """
    tz = ZoneInfo(local_timezone)
    start = query_params['start_time']
    end = query_params['end_time']
    if start.tzinfo is None:
        start = start.replace(tzinfo=datetime.timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=datetime.timezone.utc)
    local_start = start.astimezone(tz)
    local_end = end.astimezone(tz)
    return {'start_time': local_start, 'end_time': local_end}

def join_series(set_a, set_b, mode, tolerance_ms):
    """
    set_a, set_b: list of (datetime, value)
    mode: 'inner' or 'outer'
    tolerance_ms: int
    Returns list of dicts: {'timestamp', 'a', 'b'}
    """
    tol = tolerance_ms / 1000.0
    result = []
    if mode == 'inner':
        for ta, va in set_a:
            for tb, vb in set_b:
                if abs((ta - tb).total_seconds()) <= tol:
                    result.append({'timestamp': ta, 'a': va, 'b': vb})
        result.sort(key=lambda x: x['timestamp'])
    elif mode == 'outer':
        # collect all timestamps
        all_ts = set()
        for ta, _ in set_a:
            all_ts.add(ta)
        for tb, _ in set_b:
            all_ts.add(tb)
        for ts in sorted(all_ts):
            a_vals = [va for ta, va in set_a if abs((ta - ts).total_seconds()) <= tol]
            b_vals = [vb for tb, vb in set_b if abs((tb - ts).total_seconds()) <= tol]
            a_val = a_vals[0] if a_vals else None
            b_val = b_vals[0] if b_vals else None
            result.append({'timestamp': ts, 'a': a_val, 'b': b_val})
    else:
        raise ValueError("mode must be 'inner' or 'outer'")
    return result

class Subscription:
    def __init__(self, series_ids, callback):
        self.series_ids = series_ids
        self.callback = callback
        self._unsubscribed = False

    def unsubscribe(self):
        with _callbacks_lock:
            for sid in self.series_ids:
                _callbacks.get(sid, []).remove(self.callback)
        self._unsubscribed = True

def stream_updates(monitored_series, on_update_callback):
    """
    Registers callback for live updates.
    Returns Subscription object.
    """
    with _callbacks_lock:
        for sid in monitored_series:
            _callbacks.setdefault(sid, []).append(on_update_callback)
    return Subscription(monitored_series, on_update_callback)

def publish_update(series_id, datapoint):
    """
    Internal: publish a new datapoint to subscribers.
    """
    with _callbacks_lock:
        cbs = list(_callbacks.get(series_id, []))
    for cb in cbs:
        cb(series_id, datapoint)

def import_csv(csv_path, schema_definition):
    """
    Loads CSV from path, applies schema_definition mapping column to type callable.
    Returns list of dicts.
    """
    results = []
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed = {}
            for col, val in row.items():
                typ = schema_definition.get(col, str)
                parsed[col] = typ(val)
            results.append(parsed)
    return results

def record_write_history(series_id, change_details, user_email):
    """
    Adds an entry to write history.
    """
    entry = {
        'series_id': series_id,
        'change_details': change_details,
        'user_email': user_email,
        'timestamp': datetime.datetime.utcnow()
    }
    _write_history.append(entry)
    return entry

def apply_compression(series_id, strategy):
    """
    Registers compression strategy for series.
    """
    _compression_registry[series_id] = strategy
    return True

def cache_query_results(query_id, duration):
    """
    Caches a query result with expiration info.
    """
    _cache_registry[query_id] = {
        'duration': duration,
        'timestamp': datetime.datetime.utcnow()
    }
    return True

def limit_cardinality(series_id, tag_key, limit):
    """
    Sets limit on number of distinct tag values.
    """
    _cardinality_limits[(series_id, tag_key)] = limit
    _cardinality_values[(series_id, tag_key)] = set()
    return True

def add_tag_value(series_id, tag_key, value):
    """
    Adds a tag value, enforcing cardinality limit.
    """
    key = (series_id, tag_key)
    if key not in _cardinality_limits:
        raise KeyError("No cardinality limit set for series/tag")
    vals = _cardinality_values.setdefault(key, set())
    if value not in vals:
        if len(vals) >= _cardinality_limits[key]:
            raise ValueError("Cardinality limit exceeded")
        vals.add(value)
    return True
