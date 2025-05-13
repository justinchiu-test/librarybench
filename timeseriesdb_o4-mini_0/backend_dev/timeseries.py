import csv
import io
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import queue

class TimeSeriesDB:
    def __init__(self):
        self.series = {}  # series_id -> list of records
        self.history = []  # list of (series_id, timestamp, value, tags, user_id)
        self.alerts = {}  # rule_id -> dict with series_id, threshold, condition, callback
        self.streams = {}  # series_id -> list of Queue objects
        self.compression = {}  # series_id -> dict(method, block_size)
        self.cache = {}  # signature -> (result, expiry_time)
        self.cardinality_limits = {}  # series_id -> dict(tag_key -> max_values)
        self.cardinality_values = {}  # series_id -> dict(tag_key -> set of values)

    def record_write(self, series_id, timestamp, value, tags, user_id):
        # Cardinality check
        if series_id in self.cardinality_limits:
            limits = self.cardinality_limits[series_id]
            values = self.cardinality_values.setdefault(series_id, {})
            for tag_key, maxv in limits.items():
                tag_val = tags.get(tag_key)
                if tag_val is None:
                    continue
                sval = values.setdefault(tag_key, set())
                if tag_val not in sval:
                    if len(sval) >= maxv:
                        raise Exception(f"Cardinality limit exceeded for {series_id} tag {tag_key}")
                    sval.add(tag_val)
        # Store data
        rec = {"timestamp": timestamp, "value": value, "tags": tags.copy()}
        self.series.setdefault(series_id, []).append(rec)
        # History
        self.history.append((series_id, timestamp, value, tags.copy(), user_id))
        # Alerts
        for rule_id, rule in self.alerts.items():
            if rule["series_id"] == series_id:
                cond = rule["condition"]
                thr = rule["threshold"]
                if (cond == ">" and value > thr) or (cond == "<" and value < thr):
                    rule["callback"](rule_id, series_id, rec)
        # Streams
        for q in self.streams.get(series_id, []):
            q.put(rec)

    def export_csv(self, series_ids, start, end, tags_filter):
        output = io.StringIO()
        writer = None
        records = []
        tag_keys = set()
        for sid in series_ids:
            for rec in self.series.get(sid, []):
                ts = rec["timestamp"]
                if ts < start or ts > end:
                    continue
                ok = True
                for k, v in tags_filter.items():
                    if rec["tags"].get(k) != v:
                        ok = False
                        break
                if not ok:
                    continue
                rec2 = {
                    "series_id": sid,
                    "timestamp": ts,
                    "tags": rec["tags"],
                    "value": rec["value"]
                }
                records.append(rec2)
                tag_keys.update(rec["tags"].keys())
        tag_keys = sorted(tag_keys)
        header = ["series_id", "timestamp"] + tag_keys + ["value"]
        writer = csv.writer(output)
        writer.writerow(header)
        for rec in sorted(records, key=lambda x: (x["timestamp"], x["series_id"])):
            row = [rec["series_id"], x := rec["timestamp"].isoformat()]
            for k in tag_keys:
                row.append(rec["tags"].get(k, ""))
            row.append(rec["value"])
            writer.writerow(row)
        return output.getvalue()

    def define_alert(self, rule_id, series_id, threshold, condition, callback):
        self.alerts[rule_id] = {
            "series_id": series_id,
            "threshold": threshold,
            "condition": condition,
            "callback": callback
        }

    def convert_timezone(self, query, target_tz):
        start = query["start"]
        end = query["end"]
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        tz = ZoneInfo(target_tz)
        return {
            "start": start.astimezone(tz),
            "end": end.astimezone(tz)
        }

    def join_series(self, primary_id, other_ids, join_type):
        def collect(sid):
            return {rec["timestamp"]: rec["value"] for rec in self.series.get(sid, [])}
        primary = collect(primary_id)
        others = {sid: collect(sid) for sid in other_ids}
        if join_type == "inner":
            ts = set(primary.keys())
            for d in others.values():
                ts &= set(d.keys())
        elif join_type == "left":
            ts = set(primary.keys())
        elif join_type == "outer":
            ts = set(primary.keys())
            for d in others.values():
                ts |= set(d.keys())
        else:
            raise NotImplementedError(f"Join type {join_type} not supported")
        result = []
        for t in sorted(ts):
            row = {"timestamp": t, primary_id: primary.get(t)}
            for sid, d in others.items():
                row[sid] = d.get(t)
            result.append(row)
        return result

    def stream_updates(self, series_id):
        q = queue.Queue()
        self.streams.setdefault(series_id, []).append(q)
        return q

    def import_csv(self, file_path, mapping_config):
        with open(file_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if "series_id" in mapping_config:
                    sid = row[mapping_config["series_id"]]
                else:
                    sid = mapping_config.get("fixed_series_id")
                ts = datetime.fromisoformat(row[mapping_config["timestamp"]])
                val = float(row[mapping_config["value"]])
                tagsmap = {}
                for tagk, col in mapping_config.get("tags", {}).items():
                    tagsmap[tagk] = row.get(col)
                self.record_write(sid, ts, val, tagsmap, user_id="import")

    def apply_compression(self, series_id, method, block_size):
        self.compression[series_id] = {"method": method, "block_size": block_size}

    def cache_query(self, query_signature, ttl):
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    now = time.time()
                except RecursionError:
                    # If time.time is recursively patched, force expiry
                    now = float('inf')
                if query_signature in self.cache:
                    result, expiry = self.cache[query_signature]
                    if expiry > now:
                        return result
                result = func(*args, **kwargs)
                self.cache[query_signature] = (result, now + ttl)
                return result
            return wrapper
        return decorator

    def limit_cardinality(self, series_id, tag_key, max_values):
        self.cardinality_limits.setdefault(series_id, {})[tag_key] = max_values
        self.cardinality_values.setdefault(series_id, {}).setdefault(tag_key, set())
