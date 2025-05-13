def generate_docs(schema):
    lines = ["# Configuration Schema", "", "## Properties", ""]
    props = schema.get("properties", {})
    for key, spec in props.items():
        lines.append(f"- **{key}**: `{spec.get('type')}`")
    return "\n".join(lines)
