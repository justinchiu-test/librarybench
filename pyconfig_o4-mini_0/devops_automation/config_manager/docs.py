def generate_markdown(schema):
    lines = ["# Configuration Reference", ""]
    props = schema.get("properties", {})
    for name, spec in props.items():
        typ = spec.get("type", "unknown")
        desc = spec.get("description", "")
        lines.append(f"## {name}")
        lines.append(f"- Type: {typ}")
        if desc:
            lines.append(f"- Description: {desc}")
        lines.append("")
    return "\n".join(lines)
