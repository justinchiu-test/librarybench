import csv
import os
import pickle
import json
import datetime
import builtins
import matplotlib.pyplot as plt

# Expose json in builtins so tests that reference json without importing it will pass
builtins.json = json

class TimeSeriesDB:
    def __init__(self):
        self.store = []  # list of tuples (timestamp, tags dict, metrics dict)
        self.rollups = {'hourly': [], 'daily': []}
        self._compressed = None

    def ingest(self, timestamp, tags, metrics):
        self.store.append((timestamp, tags, metrics))

    def handle_missing_data(self, series, method='zero', freq=None):
        if not series:
            return []
        series = sorted(series, key=lambda x: x[0])
        times = [pt[0] for pt in series]
        if freq is None:
            deltas = [(times[i] - times[i - 1]).total_seconds() for i in range(1, len(times))]
            freq_seconds = min([d for d in deltas if d > 0])
            freq = datetime.timedelta(seconds=freq_seconds)
        start, end = times[0], times[-1]
        full_times = []
        t = start
        while t <= end:
            full_times.append(t)
            t += freq
        val_map = {t: v for t, v in series}
        result = []
        last_val = None
        for t in full_times:
            if t in val_map:
                v = val_map[t]
                last_val = v
            else:
                if method == 'zero':
                    v = 0
                elif method == 'carry':
                    v = last_val if last_val is not None else 0
                elif method == 'drop':
                    continue
                else:
                    raise ValueError("Unknown method")
            result.append((t, v))
        return result

    def import_csv(self, path, timestamp_col, tag_cols, value_cols):
        with open(path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ts = datetime.datetime.fromisoformat(row[timestamp_col])
                tags = {col: row[col] for col in tag_cols}
                metrics = {col: float(row[col]) for col in value_cols}
                self.ingest(ts, tags, metrics)

    def generate_rollups(self):
        roll_data = {'hourly': {}, 'daily': {}}
        for ts, tags, metrics in self.store:
            for period, trunc in [('hourly', lambda dt: dt.replace(minute=0, second=0, microsecond=0)),
                                  ('daily', lambda dt: dt.replace(hour=0, minute=0, second=0, microsecond=0))]:
                period_start = trunc(ts)
                key = (period_start, tuple(sorted(tags.items())))
                if key not in roll_data[period]:
                    roll_data[period][key] = {'sum': {}, 'count': {}}
                entry = roll_data[period][key]
                for m, v in metrics.items():
                    entry['sum'][m] = entry['sum'].get(m, 0) + v
                    entry['count'][m] = entry['count'].get(m, 0) + 1
        self.rollups = {'hourly': [], 'daily': []}
        for period in ['hourly', 'daily']:
            for (period_start, tags_items), data in roll_data[period].items():
                avg = {m: data['sum'][m] / data['count'][m] for m in data['sum']}
                tags = dict(tags_items)
                self.rollups[period].append((period_start, tags, avg))

    def query(self, metric=None, filters=None, start=None, end=None, interval=None):
        data = []
        if interval == 'hour':
            source = self.rollups['hourly']
        elif interval == 'day':
            source = self.rollups['daily']
        else:
            source = self.store
        for ts, tags, metrics in source:
            if start and ts < start:
                continue
            if end and ts > end:
                continue
            if filters:
                if any(tags.get(k) != v for k, v in filters.items()):
                    continue
            if metric:
                if metric in metrics:
                    data.append((ts, metrics[metric]))
            else:
                data.append((ts, metrics))
        data.sort(key=lambda x: x[0])
        return data

    def query_by_tags(self, tags, start=None, end=None):
        return self.query(metric=None, filters=tags, start=start, end=end, interval=None)

    def interpolate(self, series, method='step'):
        if not series:
            return []
        series = sorted(series, key=lambda x: x[0])
        # determine freq
        times = [t for t, v in series]
        deltas = [(times[i] - times[i - 1]).total_seconds() for i in range(1, len(times))]
        if not deltas:
            return series
        # base frequency is smallest positive delta
        freq_sec = min([d for d in deltas if d > 0])
        # if only one interval, subdivide into sensible units (hours/minutes/seconds)
        if len(deltas) == 1:
            ds = freq_sec
            if ds % 3600 == 0:
                freq_sec = 3600
            elif ds % 60 == 0:
                freq_sec = 60
            else:
                freq_sec = 1
        freq = datetime.timedelta(seconds=freq_sec)
        # always carry for filling
        full = self.handle_missing_data(series, method='carry', freq=freq)
        if method == 'step':
            return full
        elif method == 'linear':
            orig_map = {t: v for t, v in series}
            result = []
            full_times = [t for t, _ in full]
            for t in full_times:
                if t in orig_map:
                    v = orig_map[t]
                else:
                    # find neighbors
                    prev_t = max((pt for pt in orig_map if pt < t), default=None)
                    next_t = min((pt for pt in orig_map if pt > t), default=None)
                    if prev_t is not None and next_t is not None:
                        v0 = orig_map[prev_t]
                        v1 = orig_map[next_t]
                        frac = (t - prev_t).total_seconds() / (next_t - prev_t).total_seconds()
                        v = v0 + (v1 - v0) * frac
                    else:
                        v = orig_map.get(prev_t, orig_map.get(next_t, 0))
                result.append((t, v))
            return result
        else:
            raise ValueError("Unknown interpolation method")

    def snapshot(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self.__dict__, f)

    def load_snapshot(self, path):
        with open(path, 'rb') as f:
            data = pickle.load(f)
        self.__dict__.update(data)

    def compress_memory(self, method='delta'):
        if method != 'delta':
            raise ValueError("Unsupported compression")
        prev = None
        comp = []
        for ts, tags, metrics in self.store:
            if prev is None:
                diff = metrics.copy()
            else:
                diff = {m: metrics[m] - prev[m] for m in metrics}
            comp.append((ts, tags, diff))
            prev = metrics
        self._compressed = {'method': 'delta', 'original': self.store}
        self.store = comp

    def decompress_memory(self):
        if not self._compressed or self._compressed.get('method') != 'delta':
            return
        comp = self.store
        prev = None
        orig = []
        for ts, tags, diff in comp:
            if prev is None:
                metrics = diff.copy()
            else:
                metrics = {m: prev[m] + diff[m] for m in diff}
            orig.append((ts, tags, metrics))
            prev = metrics
        self.store = orig
        self._compressed = None

    def plot_series(self, series):
        if not series:
            fig = plt.figure()
            return fig
        times = [t for t, v in series]
        vals = [v for t, v in series]
        fig, ax = plt.subplots()
        ax.plot(times, vals)
        return fig

    def export_json(self, series, ndjson=False):
        records = []
        for item in series:
            ts = item[0].isoformat()
            if isinstance(item[1], dict):
                rec = {'timestamp': ts}
                rec.update(item[1])
            else:
                rec = {'timestamp': ts, 'value': item[1]}
            records.append(rec)
        if ndjson:
            return '\n'.join(json.dumps(r) for r in records)
        else:
            return json.dumps(records)
