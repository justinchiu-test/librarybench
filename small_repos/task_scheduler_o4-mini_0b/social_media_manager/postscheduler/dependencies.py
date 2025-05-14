def define_dependency(deps):
    """
    deps: dict mapping node -> list of dependencies
    returns topologically sorted list or raises ValueError on cycle
    """
    res = []
    temp = set()
    visited = set()
    def visit(n):
        if n in temp:
            raise ValueError("Cycle detected")
        if n not in visited:
            temp.add(n)
            for m in deps.get(n, []):
                visit(m)
            temp.remove(n)
            visited.add(n)
            res.append(n)
    for node in deps:
        visit(node)
    return res
