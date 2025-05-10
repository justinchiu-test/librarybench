def generate_docs(spec, formats=None):
    if formats is None:
        formats = ["md"]
    out = {}
    for fmt in formats:
        if fmt == "md":
            lines = ["# CLI Documentation"]
            for cmd, desc in spec.items():
                lines.append(f"## {cmd}\n{desc}")
            out["md"] = "\n\n".join(lines)
        elif fmt == "rst":
            lines = ["CLI Documentation", "================="]
            for cmd, desc in spec.items():
                lines.append(f"{cmd}\n{'-'*len(cmd)}\n{desc}")
            out["rst"] = "\n\n".join(lines)
        elif fmt == "html":
            lines = ["<h1>CLI Documentation</h1>", "<ul>"]
            for cmd, desc in spec.items():
                lines.append(f"<li><strong>{cmd}</strong>: {desc}</li>")
            lines.append("</ul>")
            out["html"] = "\n".join(lines)
        elif fmt == "man":
            lines = [".TH CLI 1", ".SH COMMANDS"]
            for cmd, desc in spec.items():
                lines.append(f".TP\n.B {cmd}\n{desc}")
            out["man"] = "\n".join(lines)
    return out
