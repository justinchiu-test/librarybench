import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class TimeSeriesToolkit:
    def __init__(self):
        self.data = pd.DataFrame()
        self.rollups = {}
        self.snapshots = {}
        self.compressed = {}

    def import_csv(self, filepath, timestamp_col='timestamp'):
        df = pd.read_csv(filepath)
        df[timestamp_col] = pd.to_datetime(df[timestamp_col])
        df = df.set_index(timestamp_col).sort_index()
        self.data = df
        return self.data

    def handle_missing_data(self, strategy='zero'):
        if strategy == 'zero':
            self.data = self.data.fillna(0)
        elif strategy == 'carry_forward':
            self.data = self.data.ffill()
        elif strategy == 'drop':
            self.data = self.data.dropna()
        else:
            raise ValueError("Unknown strategy")
        return self.data

    def generate_rollups(self):
        # hourly and daily aggregates (mean)
        hourly = self.data.resample('H').mean()
        daily = self.data.resample('D').mean()
        if not self.data.empty:
            # build a full daily index covering the actual days present
            start = self.data.index.min().normalize()
            end = self.data.index.max().normalize()
            full_daily_idx = pd.date_range(start, end, freq='D')
            daily = daily.reindex(full_daily_idx)
        self.rollups['hourly'] = hourly
        self.rollups['daily'] = daily
        return self.rollups

    def query(self, query_str):
        return self.data.query(query_str)

    def query_by_tags(self, device_id=None, location=None, start=None, end=None):
        df = self.data
        if device_id is not None:
            df = df[df['device_id'] == device_id]
        if location is not None:
            df = df[df['location'] == location]
        if start is not None:
            df = df[df.index >= pd.to_datetime(start)]
        if end is not None:
            df = df[df.index <= pd.to_datetime(end)]
        return df

    def interpolate(self, method='linear', order=3):
        if method == 'linear':
            self.data = self.data.interpolate(method='linear')
        elif method == 'step':
            self.data = self.data.interpolate(method='pad')
        elif method == 'spline':
            try:
                self.data = self.data.interpolate(method='spline', order=order)
            except Exception:
                # fallback to linear + forward/backward fill
                self.data = (self.data.interpolate(method='linear')
                                     .ffill()
                                     .bfill())
        else:
            raise ValueError("Unknown interpolation method")
        return self.data

    def snapshot(self, name):
        self.snapshots[name] = self.data.copy()

    def compress_memory(self):
        num_cols = self.data.select_dtypes(include=[np.number]).columns
        non_cols = [col for col in self.data.columns if col not in num_cols]
        comp = {'numeric': {}, 'non_numeric': {}}
        for col in num_cols:
            vals = self.data[col].values
            if len(vals) == 0:
                comp['numeric'][col] = {'first': None, 'deltas': []}
            else:
                first = vals[0].tolist() if hasattr(vals[0], 'tolist') else vals[0]
                deltas = np.diff(vals).tolist()
                comp['numeric'][col] = {'first': first, 'deltas': deltas}
        for col in non_cols:
            comp['non_numeric'][col] = self.data[col].tolist()
        freq = getattr(self.data.index, 'freqstr', None)
        comp['index_freq'] = freq
        comp['index'] = [ts.isoformat() for ts in self.data.index]
        self.compressed = comp
        return comp

    def decompress_memory(self):
        comp = self.compressed
        idx_list = comp.get('index', [])
        idx = pd.to_datetime(idx_list)
        freq = comp.get('index_freq', None)
        if freq is not None:
            try:
                idx = pd.DatetimeIndex(idx, freq=freq)
            except Exception:
                pass
        recon = {}
        for col, data in comp.get('numeric', {}).items():
            first = data['first']
            deltas = data['deltas']
            if first is None:
                recon[col] = []
            else:
                vals = [first]
                for d in deltas:
                    vals.append(vals[-1] + d)
                recon[col] = vals
        for col, vals in comp.get('non_numeric', {}).items():
            recon[col] = vals
        df = pd.DataFrame(recon, index=idx)
        return df

    def plot_series(self):
        fig, axes = plt.subplots(2, 1, figsize=(8, 6))
        if not self.data.empty:
            self.data.plot(ax=axes[0], title='Raw Data')
        if self.rollups:
            for key, df in self.rollups.items():
                df.plot(ax=axes[1], label=key)
            axes[1].legend()
            axes[1].set_title('Rollups')
        plt.tight_layout()
        return fig

    def export_json(self, data=None):
        df = self.data if data is None else data
        return df.reset_index().to_json(orient='records')
