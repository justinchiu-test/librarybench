def generate_docs(commands):
    md = "# Commands\n" + "\n".join(f"- {c}" for c in commands)
    html = "<h1>Commands</h1>" + "".join(f"<p>{c}</p>" for c in commands)
    rst = "Commands\n" + "="*8 + "\n" + "\n".join(f"- {c}" for c in commands)
    man = "COMMANDS\n" + "\n".join(commands)
    return {"md": md, "html": html, "rst": rst, "man": man}
