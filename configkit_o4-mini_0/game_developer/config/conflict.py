class ConflictReporter:
    @staticmethod
    def detect(transitions):
        """
        transitions: dict of state -> next_state or list of next_states
        Detect mutual transitions of length 2.
        """
        conflicts = []
        for a, nexts in transitions.items():
            if isinstance(nexts, (list, tuple)):
                for b in nexts:
                    if b in transitions:
                        nb = transitions[b]
                        if (isinstance(nb, (list, tuple)) and a in nb) or (nb == a):
                            pair = tuple(sorted([a, b]))
                            if pair not in conflicts:
                                conflicts.append(pair)
            else:
                b = nexts
                if b in transitions and transitions[b] == a:
                    pair = tuple(sorted([a, b]))
                    if pair not in conflicts:
                        conflicts.append(pair)
        return conflicts
