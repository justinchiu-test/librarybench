def visualize(nodes, edges):
    lines = ["digraph G {"]
    for n in nodes:
        lines.append(f'  "{n}";')
    for src, dst in edges:
        lines.append(f'  "{src}" -> "{dst}";')
    lines.append("}")
    return "\n".join(lines)
