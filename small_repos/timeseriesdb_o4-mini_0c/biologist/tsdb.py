import csv
import io
import threading
import functools
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

# In-memory stores
_series_data = {}
_audit_trail = []
_cache = {}
_cardinality = {}

def import_csv(path, mapping):
    """
    Load bulk CSV exports from sequencers and metabolomics instruments.
    mapping: dict mapping source column names to internal names
    """
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            internal = {}
            for col, val in row.items():
                key = mapping.get(col, col)
                if key == 'time':
                    # parse ISO format
                    val = datetime.fromisoformat(val)
                internal[key] = val
            exp_id = internal.get('experiment_id')
            if exp_id is None:
                continue
            _series_data.setdefault(exp_id, []).append(internal)
    return True

def export_csv(experiment_ids, time_range, include_metadata):
    """
    Produce CSVs of multi-omics series for downstream analysis.
    time_range: (start_datetime, end_datetime)
    """
    start, end = time_range
    output = io.StringIO()
    # determine all metadata keys if needed
    meta_keys = set()
    if include_metadata:
        for exp in experiment_ids:
            for row in _series_data.get(exp, []):
                for k in row:
                    if k not in ('experiment_id', 'time', 'value'):
                        meta_keys.add(k)
    fieldnames = ['experiment_id', 'time', 'value'] + sorted(meta_keys)
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for exp in experiment_ids:
        for row in _series_data.get(exp, []):
            t = row['time']
            if start <= t <= end:
                out = {
                    'experiment_id': exp,
                    'time': t.isoformat(),
                    'value': row.get('value')
                }
                if include_metadata:
                    for k in meta_keys:
                        out[k] = row.get(k)
                writer.writerow(out)
    return output.getvalue()

def define_alert(biomarker_series, condition, threshold, recipients):
    """
    Email or trigger when a biomarker crosses a critical threshold.
    Returns list of recipients to alert (empty if none).
    """
    triggered = False
    for entry in biomarker_series:
        val = entry.get('value')
        if val is None:
            continue
        if condition == '>' and val > threshold:
            triggered = True
            break
        if condition == '<' and val < threshold:
            triggered = True
            break
    return recipients if triggered else []

def convert_timezone(query, lab_tz):
    """
    Convert all UTC timestamps to local lab time.
    query: list of dicts with 'time' datetime in UTC.
    lab_tz: timezone string
    """
    tz = ZoneInfo(lab_tz)
    converted = []
    for row in query:
        t = row['time']
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)
        local = t.astimezone(tz)
        new = row.copy()
        new['time'] = local
        converted.append(new)
    return converted

def join_series(expression_series, phenotype_series, join_mode):
    """
    Align transcriptomics and phenotypic data by sample time.
    join_mode: 'inner' or 'outer'
    """
    expr_map = {r['time']: r.get('value') for r in expression_series}
    pheno_map = {r['time']: r.get('value') for r in phenotype_series}
    times = set(expr_map.keys()) & set(pheno_map.keys()) if join_mode == 'inner' else set(expr_map.keys()) | set(pheno_map.keys())
    result = []
    for t in sorted(times):
        result.append({
            'time': t,
            'expression': expr_map.get(t),
            'phenotype': pheno_map.get(t)
        })
    return result

def stream_updates(sample_series):
    """
    Generator for live feeds as new measurements arrive.
    """
    for item in sample_series:
        yield item

def record_version(entry, user_id, change_reason):
    """
    Maintain history of data edits for reproducible science.
    """
    rec = {
        'entry': entry,
        'user_id': user_id,
        'change_reason': change_reason,
        'timestamp': datetime.now(timezone.utc)
    }
    _audit_trail.append(rec)
    return True

def apply_compression(series_id, method):
    """
    Compress large dense time series.
    method: 'gzip', 'lz4', or 'none'
    """
    if method not in ('gzip', 'lz4', 'none'):
        raise ValueError(f"Unsupported compression method: {method}")
    data = f"{series_id}:{method}".encode()
    return data

def cache_query(query_signature, ttl):
    """
    Decorator factory to cache expensive joins or aggregations.
    """
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            now = datetime.now(timezone.utc)
            entry = _cache.get(query_signature)
            if entry:
                result, expire = entry
                if now < expire:
                    return result
            res = fn(*args, **kwargs)
            _cache[query_signature] = (res, now + timedelta(seconds=ttl))
            return res
        return wrapper
    return decorator

def limit_cardinality(series_id, tag_key, max_count):
    """
    Cap unique sample metadata combinations.
    """
    _cardinality.setdefault(series_id, {})[tag_key] = max_count
    return True
