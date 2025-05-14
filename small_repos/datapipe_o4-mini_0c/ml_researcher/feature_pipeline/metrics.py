try:
    # if prometheus_client is installed, use it
    from prometheus_client import CollectorRegistry, Counter, Summary
except ImportError:
    # minimal stand-in implementations
    class CollectorRegistry:
        def __init__(self):
            self._metrics = {}

        def register_metric(self, name, metric):
            self._metrics[name] = metric

        def collect(self):
            # Return dummy families with only the .name attribute
            class DummyFamily:
                def __init__(self, name):
                    self.name = name

            return [DummyFamily(name) for name in self._metrics.keys()]

        def get_sample_value(self, name, labels=None):
            m = self._metrics.get(name)
            if m is None:
                return None
            # assume metric provides .get()
            return m.get()

    class Counter:
        def __init__(self, name, documentation, registry=None):
            self.name = name
            self._value = 0.0
            if registry is not None:
                registry.register_metric(name, self)

        def inc(self, amount=1):
            self._value += amount

        def get(self):
            return self._value

    class Summary:
        def __init__(self, name, documentation, registry=None):
            self.name = name
            self._observations = []
            if registry is not None:
                registry.register_metric(name, self)

        def observe(self, value):
            self._observations.append(value)

class PrometheusMetrics:
    def __init__(self):
        self.registry = CollectorRegistry()
        self.counters = {}
        self.summaries = {}

    def inc(self, name, amount=1):
        if name not in self.counters:
            # note: registry registration happens in our Counter/__init__
            self.counters[name] = Counter(name, name, registry=self.registry)
        self.counters[name].inc(amount)

    def observe(self, name, value):
        if name not in self.summaries:
            self.summaries[name] = Summary(name, name, registry=self.registry)
        self.summaries[name].observe(value)
