import re
import subprocess

SEMVER_RE = re.compile(r'^v?(\d+)\.(\d+)\.(\d+)$')

def bump_version():
    # Get all tags sorted by version desc
    result = subprocess.run(['git', 'tag', '--sort=-v:refname'], capture_output=True, text=True, check=True)
    tags = [t.strip() for t in result.stdout.splitlines() if t.strip()]
    latest = tags[0] if tags else 'v0.0.0'
    m = SEMVER_RE.match(latest)
    if not m:
        raise ValueError(f'Invalid tag format: {latest}')
    major, minor, patch = map(int, m.groups())
    patch += 1
    new_version = f'{major}.{minor}.{patch}'
    tag_name = f'v{new_version}'
    subprocess.run(['git', 'tag', '-a', tag_name, '-m', f'Release {tag_name}'], check=True)
    return new_version
