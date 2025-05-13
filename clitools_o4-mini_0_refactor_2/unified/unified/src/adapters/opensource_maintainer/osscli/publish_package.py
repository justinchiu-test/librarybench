"""
Package publishing for Open Source Maintainer CLI.
"""
def publish_package(to_pypi=False, to_github=False):
    return {"pypi": bool(to_pypi), "github": bool(to_github)}