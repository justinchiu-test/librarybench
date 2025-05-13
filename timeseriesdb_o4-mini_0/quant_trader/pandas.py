import csv
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Minimal Series class to support element‐wise ops and .dt
class Series:
    def __init__(self, data):
        self.data = list(data)
        self.tz = None

    @property
    def dt(self):
        return self

    def tz_convert(self, tz):
        tzinfo = tz if isinstance(tz, ZoneInfo) else ZoneInfo(tz)
        new_data = []
        for dt in self.data:
            # ensure dt is timezone‐aware
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=ZoneInfo("UTC"))
            new_data.append(dt.astimezone(tzinfo))
        out = Series(new_data)
        out.tz = tzinfo
        return out

    # comparison ops
    def __ge__(self, other):
        if isinstance(other, Series):
            odata = other.data
        else:
            odata = [other] * len(self.data)
        return Series([a >= b for a, b in zip(self.data, odata)])

    def __le__(self, other):
        if isinstance(other, Series):
            odata = other.data
        else:
            odata = [other] * len(self.data)
        return Series([a <= b for a, b in zip(self.data, odata)])

    def __gt__(self, other):
        if isinstance(other, Series):
            odata = other.data
        else:
            odata = [other] * len(self.data)
        return Series([a > b for a, b in zip(self.data, odata)])

    def __lt__(self, other):
        if isinstance(other, Series):
            odata = other.data
        else:
            odata = [other] * len(self.data)
        return Series([a < b for a, b in zip(self.data, odata)])

    def __eq__(self, other):
        if isinstance(other, Series):
            odata = other.data
        else:
            odata = [other] * len(self.data)
        return Series([a == b for a, b in zip(self.data, odata)])

    def __and__(self, other):
        if isinstance(other, Series):
            odata = other.data
        else:
            odata = list(other)
        return Series([a and b for a, b in zip(self.data, odata)])

    def __len__(self):
        return len(self.data)

# Locator for df.loc[mask]
class DataFrameLoc:
    def __init__(self, df):
        self._df = df

    def __getitem__(self, mask):
        if isinstance(mask, Series):
            m = mask.data
        else:
            m = mask
        new_rows = []
        for keep, row in zip(m, self._df.rows):
            if keep:
                new_rows.append(row.copy())
        return DataFrame(rows=new_rows, columns=self._df.columns)

# Locator for df.iloc[i]
class DataFrameILoc:
    def __init__(self, df):
        self._df = df

    def __getitem__(self, idx):
        return self._df.rows[idx]

# Minimal DataFrame
class DataFrame:
    def __init__(self, data=None, rows=None, columns=None):
        if data is not None:
            # data is dict of column -> list
            self.columns = list(data.keys())
            n = len(next(iter(data.values())))
            self.rows = []
            for i in range(n):
                row = {}
                for c in self.columns:
                    row[c] = data[c][i]
                self.rows.append(row)
        else:
            self.rows = [r.copy() for r in (rows or [])]
            if columns is not None:
                self.columns = columns.copy()
            else:
                # infer
                self.columns = list(self.rows[0].keys()) if self.rows else []

    def copy(self):
        return DataFrame(rows=self.rows, columns=self.columns)

    def sort_values(self, by):
        new_rows = sorted(self.rows, key=lambda r: r.get(by))
        return DataFrame(rows=new_rows, columns=self.columns)

    def __setitem__(self, key, value):
        if isinstance(value, Series):
            for i, row in enumerate(self.rows):
                row[key] = value.data[i]
        else:
            for row in self.rows:
                row[key] = value
        if key not in self.columns:
            self.columns.append(key)

    def __getitem__(self, key):
        # If key is a list of columns, return a DataFrame slice
        if isinstance(key, list):
            out_rows = []
            for row in self.rows:
                nr = {}
                for c in key:
                    nr[c] = row.get(c)
                out_rows.append(nr)
            return DataFrame(rows=out_rows, columns=key)
        # Single-column access returns a Series
        else:
            data = [row.get(key) for row in self.rows]
            s = Series(data)
            # Preserve timezone metadata if values are tz-aware datetimes
            if data:
                first = data[0]
                if isinstance(first, datetime) and first.tzinfo is not None:
                    s.tz = first.tzinfo
            return s

    @property
    def loc(self):
        return DataFrameLoc(self)

    @property
    def iloc(self):
        return DataFrameILoc(self)

    def dropna(self, axis=0, subset=None):
        new_rows = []
        for row in self.rows:
            if not any(row.get(k) is None for k in subset):
                new_rows.append(row.copy())
        return DataFrame(rows=new_rows, columns=self.columns)

    def to_csv(self, index=False):
        # header
        lines = [",".join(self.columns)]
        for row in self.rows:
            vals = []
            for c in self.columns:
                v = row.get(c)
                if isinstance(v, datetime):
                    vals.append(v.isoformat())
                elif v is None:
                    vals.append("")
                else:
                    vals.append(str(v))
            lines.append(",".join(vals))
        return "\n".join(lines) + "\n"

    def __len__(self):
        return len(self.rows)

# read_csv
def read_csv(filepath):
    rows = []
    with open(filepath, newline="") as f:
        r = csv.DictReader(f)
        cols = r.fieldnames
        for rec in r:
            nr = {}
            for k, v in rec.items():
                if v == "" or v is None:
                    nr[k] = None
                else:
                    # try int, float, else leave
                    try:
                        nr[k] = int(v)
                    except:
                        try:
                            nr[k] = float(v)
                        except:
                            nr[k] = v
            rows.append(nr)
    return DataFrame(rows=rows, columns=cols)

# to_datetime
def to_datetime(arg, utc=False):
    if isinstance(arg, Series):
        data = arg.data
    else:
        data = list(arg)
    out = []
    for v in data:
        if isinstance(v, datetime):
            dt = v
        else:
            s = v
            if isinstance(s, str) and s.endswith("Z"):
                s2 = s.rstrip("Z")
                dt = datetime.fromisoformat(s2)
                dt = dt.replace(tzinfo=ZoneInfo("UTC"))
            else:
                dt = datetime.fromisoformat(s)
        if utc and dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo("UTC"))
        out.append(dt)
    s = Series(out)
    if utc:
        s.tz = ZoneInfo("UTC")
    return s

# Timedelta stub
class Timedelta:
    def __init__(self, arg):
        if isinstance(arg, Timedelta):
            self.delta = arg.delta
        elif isinstance(arg, (int, float)):
            self.delta = timedelta(seconds=arg)
        elif isinstance(arg, timedelta):
            self.delta = arg
        else:
            # string like "1s"
            s = str(arg)
            if s.endswith("s"):
                secs = int(s[:-1])
                self.delta = timedelta(seconds=secs)
            else:
                self.delta = timedelta(seconds=int(s))

# concat stub
def concat(dfs, ignore_index=False):
    cols = []
    rows = []
    for df in dfs:
        for c in df.columns:
            if c not in cols:
                cols.append(c)
        for r in df.rows:
            rows.append(r.copy())
    return DataFrame(rows=rows, columns=cols)

# merge_asof stub
def merge_asof(left, right, on, tolerance, direction="forward", suffixes=("_l","_r")):
    tol = tolerance.delta if hasattr(tolerance, "delta") else tolerance
    new_rows = []
    for lrow in left.rows:
        base = lrow[on]
        best = None
        best_diff = None
        for rrow in right.rows:
            diff = rrow[on] - base
            if direction == "forward":
                if diff >= timedelta(0) and diff <= tol:
                    if best_diff is None or diff < best_diff:
                        best_diff = diff
                        best = rrow
            elif direction == "nearest":
                d2 = abs(diff)
                if d2 <= tol:
                    if best_diff is None or d2 < best_diff:
                        best_diff = d2
                        best = rrow
        nr = lrow.copy()
        for c in right.columns:
            if c == on:
                continue
            nr[c] = best[c] if best is not None else None
        new_rows.append(nr)
    # combine columns
    new_cols = list(left.columns)
    for c in right.columns:
        if c != on and c not in new_cols:
            new_cols.append(c)
    return DataFrame(rows=new_rows, columns=new_cols)

# expose API
DataFrame = DataFrame
Series = Series
read_csv = read_csv
to_datetime = to_datetime
Timedelta = Timedelta
concat = concat
merge_asof = merge_asof

# testing submodule
class _testing:
    @staticmethod
    def assert_frame_equal(df1, df2):
        if df1.columns != df2.columns:
            raise AssertionError(f"Columns differ {df1.columns} != {df2.columns}")
        if len(df1.rows) != len(df2.rows):
            raise AssertionError(f"Row count differ {len(df1.rows)} != {len(df2.rows)}")
        for i, (r1, r2) in enumerate(zip(df1.rows, df2.rows)):
            for c in df1.columns:
                v1 = r1.get(c)
                v2 = r2.get(c)
                if isinstance(v1, datetime) and isinstance(v2, datetime):
                    if v1.isoformat() != v2.isoformat():
                        raise AssertionError(f"At row {i}, col {c}: {v1} != {v2}")
                else:
                    if v1 != v2:
                        raise AssertionError(f"At row {i}, col {c}: {v1} != {v2}")

testing = _testing()
