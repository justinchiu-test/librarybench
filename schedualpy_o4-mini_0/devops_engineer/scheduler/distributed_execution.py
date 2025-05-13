import threading

class DistributedExecution:
    def __init__(self, nodes=None):
        self.nodes = nodes or []
        self.leader = None
        self._lock = threading.Lock()

    def add_node(self, node):
        with self._lock:
            self.nodes.append(node)

    def elect_leader(self):
        with self._lock:
            if not self.nodes:
                self.leader = None
            else:
                # deterministic leader election: lowest node id/name
                self.leader = sorted(self.nodes)[0]
            return self.leader

    def start(self):
        # placeholder for starting the scheduler instance
        return True

    def stop(self):
        # placeholder for stopping the scheduler instance
        return True
