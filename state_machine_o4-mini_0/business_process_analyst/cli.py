from process_engine import Machine

_machines = {}
_next_id = 1

def scaffold_process():
    global _next_id
    m = Machine()
    pid = _next_id
    _machines[pid] = m
    _next_id += 1
    return pid

def dump_state(process_id):
    m = _machines.get(process_id)
    if not m:
        raise ValueError("Process not found")
    return m.current_state
