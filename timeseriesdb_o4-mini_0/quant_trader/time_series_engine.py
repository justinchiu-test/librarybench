import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import gzip
import pickle
import zlib
import threading
import queue
import os

# Global stores
series_quotes = {}       # series_id -> DataFrame of quotes
series_trades = {}       # series_id -> DataFrame of trades
alerts = {}              # alert_id -> alert config
audit_log = []           # list of audit entries
compressed_series = {}   # series_id -> compressed bytes
cache_store = {}         # query_id -> {'expire': datetime, 'data': any}
subscribers = {}         # series_id -> list of queue.Queue
cardinality_limits = {}  # series_id -> {tag_key: max_unique}
cardinality_values = {}  # series_id -> {tag_key: set(values)}


class StreamUpdatesIterator:
    """
    Iterator that registers a queue for streaming updates on creation,
    then yields items put into the queue.
    """
    def __init__(self, series_identifier):
        self.q = queue.Queue()
        subscribers.setdefault(series_identifier, []).append(self.q)

    def __iter__(self):
        return self

    def __next__(self):
        # Block until the next item is available
        item = self.q.get()
        return item


def export_csv(quotes_ids, start_time, end_time, field_selection):
    frames = []
    for sid in quotes_ids:
        if sid in series_quotes:
            df = series_quotes[sid].copy()
            df['series_id'] = sid
            frames.append(df)
        if sid in series_trades:
            df2 = series_trades[sid].copy()
            df2['series_id'] = sid
            frames.append(df2)
    if not frames:
        return ""
    df_all = pd.concat(frames, ignore_index=True)
    mask = (df_all['timestamp'] >= start_time) & (df_all['timestamp'] <= end_time)
    df_filtered = df_all.loc[mask]
    df_selected = df_filtered[field_selection]
    return df_selected.to_csv(index=False)


def define_alert(alert_id, series_id, operator, price_threshold, notification_target):
    alerts[alert_id] = {
        'series_id': series_id,
        'operator': operator,
        'price_threshold': price_threshold,
        'notification_target': notification_target
    }


def convert_timezone(trading_query, exchange_tz):
    # Build a minimal DataFrame from the incoming query (real or minimal pandas)
    data = {}
    # trading_query.columns should work for both real and minimal DataFrame
    for col in trading_query.columns:
        series = trading_query[col]
        # minimal Series has .data, real pandas Series is iterable
        if hasattr(series, 'data'):
            data[col] = list(series.data)
        else:
            data[col] = list(series)
    df = pd.DataFrame(data)
    # Assume naive timestamps are UTC
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df['timestamp'] = df['timestamp'].dt.tz_convert(exchange_tz)
    return df


def join_series(base_series, overlay_series, join_type, tolerance):
    # base_series and overlay_series are DataFrames with 'timestamp'
    bs = base_series.copy().sort_values('timestamp')
    os_ = overlay_series.copy().sort_values('timestamp')
    tol = pd.Timedelta(tolerance)

    # choose merge direction
    if join_type in ('left', 'inner'):
        direction = 'forward'
    elif join_type == 'outer':
        direction = 'nearest'
    else:
        raise ValueError(f"Unsupported join_type: {join_type}")

    merged = pd.merge_asof(
        bs,
        os_,
        on='timestamp',
        tolerance=tol,
        direction=direction,
        suffixes=('_base', '_ovr')
    )
    if join_type == 'inner':
        # drop rows where overlay had no match
        overlay_cols = [c for c in os_.columns if c != 'timestamp']
        merged = merged.dropna(axis=0, subset=overlay_cols)
    return merged


def stream_updates(series_identifier):
    """
    Return an iterator that yields updates pushed to a queue.
    Registration happens immediately on call.
    """
    return StreamUpdatesIterator(series_identifier)


def import_csv(historical_file, column_map):
    # Use minimal pandas read_csv which returns a minimal DataFrame
    df = pd.read_csv(historical_file)
    # Manually rename columns in the minimal DataFrame
    old_columns = df.columns
    new_columns = [column_map.get(c, c) for c in old_columns]
    new_rows = []
    for row in df.rows:
        new_row = {}
        for old_c, new_c in zip(old_columns, new_columns):
            new_row[new_c] = row.get(old_c)
        new_rows.append(new_row)
    # Build and return a new minimal DataFrame
    return pd.DataFrame(rows=new_rows, columns=new_columns)


def record_audit(series_id, operation, user, timestamp):
    audit_log.append({
        'series_id': series_id,
        'operation': operation,
        'user': user,
        'timestamp': timestamp
    })


def apply_compression(series_id, compression_type):
    if series_id not in series_quotes:
        raise KeyError("Series not found")
    df = series_quotes[series_id]
    data = pickle.dumps(df)
    if compression_type == 'gzip':
        comp = gzip.compress(data)
    elif compression_type == 'zlib':
        comp = zlib.compress(data)
    else:
        raise ValueError("Unsupported compression_type")
    compressed_series[series_id] = comp


def cache_query(query_id, valid_for_sec):
    expire = datetime.utcnow() + timedelta(seconds=valid_for_sec)
    cache_store[query_id] = {'expire': expire, 'data': None}


def limit_cardinality(series_id, tag_key, max_unique):
    limits = cardinality_limits.setdefault(series_id, {})
    limits[tag_key] = max_unique
    # initialize values set
    cardinality_values.setdefault(series_id, {}).setdefault(tag_key, set())


def add_tag_to_series(series_id, tag_key, tag_value):
    if series_id not in cardinality_limits or \
       tag_key not in cardinality_limits[series_id]:
        # no limit set, just add
        cardinality_values.setdefault(series_id, {}) \
                          .setdefault(tag_key, set()) \
                          .add(tag_value)
        return
    values = cardinality_values[series_id][tag_key]
    if tag_value not in values and \
       len(values) >= cardinality_limits[series_id][tag_key]:
        raise ValueError("Cardinality limit exceeded")
    values.add(tag_value)
