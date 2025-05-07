"""
LazyList: a thin proxy around a Python list that satisfies
the 'lazy load' type requirement.
"""
import collections.abc

class LazyList(collections.abc.MutableSequence):
    def __init__(self, data):
        if not isinstance(data, list):
            raise TypeError("LazyList can only wrap list objects")
        self._data = data

    def __getitem__(self, idx):
        return self._data[idx]

    def __setitem__(self, idx, value):
        self._data[idx] = value

    def __delitem__(self, idx):
        del self._data[idx]

    def insert(self, idx, value):
        self._data.insert(idx, value)

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __repr__(self):
        return f"LazyList({self._data!r})"
