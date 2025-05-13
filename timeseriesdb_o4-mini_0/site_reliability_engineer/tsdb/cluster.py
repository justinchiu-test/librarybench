class ClusterReplication:
    def __init__(self):
        self.peers = []

    def register(self, peer):
        self.peers.append(peer)

    def replicate(self, record):
        for peer in self.peers:
            peer.insert(record, replicate=False, wal_write=False)
