def generate_dot(fsm):
    lines = ['digraph FSM {']
    for (fr, ev), tr in fsm.transitions.items():
        lines.append(f'    "{fr}" -> "{tr["to"]}" [label="{ev}"];')
    lines.append('}')
    return '\n'.join(lines)
