class ConflictReporting:
    @staticmethod
    def detect(config):
        # Contradictory SLA: alert.threshold should be greater than error_rate
        threshold = config.get('alert', {}).get('threshold')
        error_rate = config.get('circuit_breaker', {}).get('error_rate')
        if threshold is not None and error_rate is not None:
            if threshold <= error_rate:
                raise ValueError("Contradictory SLA targets: alert.threshold <= circuit_breaker.error_rate")
        # Circular dependencies in alerts
        alerts = config.get('alerts', [])
        if not isinstance(alerts, list):
            return
        graph = {}
        for alert in alerts:
            name = alert.get('name')
            deps = alert.get('depends_on', [])
            graph[name] = deps
        visited = set()
        rec_stack = set()

        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            for nei in graph.get(node, []):
                if nei not in visited:
                    dfs(nei)
                elif nei in rec_stack:
                    raise ValueError("Circular dependency detected in alerts")
            rec_stack.remove(node)

        for node in graph:
            if node not in visited:
                dfs(node)
