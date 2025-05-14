def bump_version(version: str) -> str:
    parts = version.strip().split(".")
    if not all(p.isdigit() for p in parts):
        raise ValueError("Invalid version format")
    if len(parts) < 3:
        parts += ["0"] * (3 - len(parts))
    major, minor, patch = map(int, parts[:3])
    patch += 1
    return f"{major}.{minor}.{patch}"
