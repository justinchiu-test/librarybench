import re

def bump_version(tags):
    """
    Given a list of git tags like ['v1.2.3', 'v2.0.0'], return next patch version string 'vX.Y.Z'.
    """
    semvers = []
    pattern = re.compile(r'^v(\d+)\.(\d+)\.(\d+)$')
    for tag in tags:
        m = pattern.match(tag)
        if m:
            semvers.append(tuple(map(int, m.groups())))
    if not semvers:
        return 'v0.0.1'
    major, minor, patch = max(semvers)
    return f'v{major}.{minor}.{patch+1}'
