# documentation_gen
def generate_markdown(schema: dict) -> str:
    """
    Generate Markdown documentation from a JSON Schema.
    """
    lines = ["# Configuration Schema", ""]
    props = schema.get('properties', {})
    for name, info in props.items():
        typ = info.get('type', 'any')
        desc = info.get('description', '')
        lines.append(f"## {name}")
        lines.append(f"- Type: `{typ}`")
        if desc:
            lines.append(f"- Description: {desc}")
        lines.append("")
    return "\n".join(lines)
