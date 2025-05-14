import csv
import datetime
import time
from zoneinfo import ZoneInfo

series_data = {}
versions = []
alert_rules = {}
alert_events = []
cache_data = {}
cardinality_limits = {}
series_tag_keys = {}

def export_csv(device_ids, from_ts, to_ts, include_tags):
    output = []
    headers = ['series_id', 'timestamp', 'value']
    tag_keys = set()
    if include_tags:
        for sid in device_ids:
            for point in series_data.get(sid, []):
                if from_ts <= point['timestamp'] <= to_ts:
                    tag_keys.update(point.get('tags', {}).keys())
        tag_keys = sorted(tag_keys)
        headers += tag_keys
    output.append(','.join(headers))
    for sid in device_ids:
        for point in series_data.get(sid, []):
            ts = point['timestamp']
            if from_ts <= ts <= to_ts:
                row = [sid, ts.isoformat(), str(point['value'])]
                if include_tags:
                    for key in tag_keys:
                        row.append(str(point.get('tags', {}).get(key, '')))
                output.append(','.join(row))
    return '\n'.join(output)

def define_alert(rule_id, device_series, threshold_type, threshold_value, webhook_url):
    if threshold_type not in ('gt', 'lt', 'ge', 'le', 'eq', 'ne'):
        raise ValueError('Invalid threshold_type')
    alert_rules[rule_id] = {
        'device_series': device_series,
        'threshold_type': threshold_type,
        'threshold_value': threshold_value,
        'webhook_url': webhook_url
    }

def _check_alert(series_id, timestamp, value):
    for rule_id, rule in alert_rules.items():
        if rule['device_series'] == series_id:
            tt = rule['threshold_type']
            tv = rule['threshold_value']
            cond = False
            if tt == 'gt':
                cond = value > tv
            elif tt == 'lt':
                cond = value < tv
            elif tt == 'ge':
                cond = value >= tv
            elif tt == 'le':
                cond = value <= tv
            elif tt == 'eq':
                cond = value == tv
            elif tt == 'ne':
                cond = value != tv
            if cond:
                alert_events.append({
                    'rule_id': rule_id,
                    'series_id': series_id,
                    'timestamp': timestamp,
                    'value': value,
                    'webhook_url': rule['webhook_url']
                })

def convert_timezone(query, device_local_tz):
    tz = ZoneInfo(device_local_tz)
    from_local = query['from_ts'].replace(tzinfo=tz)
    to_local = query['to_ts'].replace(tzinfo=tz)
    from_utc = from_local.astimezone(datetime.timezone.utc)
    to_utc = to_local.astimezone(datetime.timezone.utc)
    return {'from_ts_utc': from_utc, 'to_ts_utc': to_utc}

def join_series(main_series, aux_series, join_policy):
    def to_map(series):
        return {e['timestamp']: e['value'] for e in series}
    m = to_map(main_series)
    a = to_map(aux_series)
    if join_policy == 'inner':
        ts_set = set(m.keys()) & set(a.keys())
    elif join_policy == 'left':
        ts_set = set(m.keys())
    elif join_policy == 'outer':
        ts_set = set(m.keys()) | set(a.keys())
    else:
        raise ValueError('Invalid join_policy')
    result = []
    for ts in sorted(ts_set):
        result.append({
            'timestamp': ts,
            'main': m.get(ts),
            'aux': a.get(ts)
        })
    return result

def stream_data(device_series, callback_fn):
    for point in series_data.get(device_series, []):
        callback_fn(device_series, point)

def import_csv(file, mapping_json):
    if isinstance(file, str):
        f = open(file, newline='')
        close_f = True
    else:
        f = file
        close_f = False
    reader = csv.DictReader(f)
    for row in reader:
        series_id = None
        timestamp = None
        value = None
        tags = {}
        for col, val in row.items():
            if col not in mapping_json:
                continue
            target = mapping_json[col]
            if target == 'series_id':
                series_id = val
            elif target == 'timestamp':
                timestamp = datetime.datetime.fromisoformat(val)
            elif target == 'value':
                value = float(val)
            else:
                tags[target] = val
        payload = {'value': value, 'tags': tags}
        record_version(series_id, timestamp, payload, mapping_json.get('user_agent', 'import_csv'))
    if close_f:
        f.close()

def record_version(series_id, timestamp, payload, user_agent):
    tags = payload.get('tags', {})
    if series_id in cardinality_limits:
        existing = series_tag_keys.get(series_id, set())
        new_keys = set(tags.keys()) - existing
        if len(existing) + len(new_keys) > cardinality_limits[series_id]:
            raise Exception('Cardinality limit exceeded')
        series_tag_keys.setdefault(series_id, set()).update(tags.keys())
    series_data.setdefault(series_id, []).append({
        'timestamp': timestamp,
        'value': payload.get('value'),
        'tags': tags
    })
    versions.append({
        'series_id': series_id,
        'timestamp': timestamp,
        'payload': payload,
        'user_agent': user_agent
    })
    _check_alert(series_id, timestamp, payload.get('value'))

def compress_series_in_memory(series_id, algorithm):
    data = sorted(series_data.get(series_id, []), key=lambda x: x['timestamp'])
    values = [d['value'] for d in data]
    if algorithm == 'delta':
        if not values:
            return []
        deltas = []
        prev = values[0]
        for v in values[1:]:
            deltas.append(v - prev)
            prev = v
        return deltas
    elif algorithm == 'rle':
        if not values:
            return []
        rle = []
        prev = values[0]
        count = 1
        for v in values[1:]:
            if v == prev:
                count += 1
            else:
                rle.append((prev, count))
                prev = v
                count = 1
        rle.append((prev, count))
        return rle
    else:
        raise ValueError('Unknown algorithm')

def cache_query(signature, ttl_ms):
    def decorator(func):
        def wrapper(*args, **kwargs):
            now = time.monotonic()
            entry = cache_data.get(signature)
            if entry and now < entry['expiry']:
                return entry['result']
            result = func(*args, **kwargs)
            cache_data[signature] = {'result': result, 'expiry': now + ttl_ms / 1000.0}
            return result
        return wrapper
    return decorator

def enforce_cardinality_limit(series_id, max_tags):
    cardinality_limits[series_id] = max_tags
    series_tag_keys.setdefault(series_id, set())
