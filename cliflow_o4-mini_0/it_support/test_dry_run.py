from onboarding.dry_run import run_dry_run

@run_dry_run
def install_packages(packages, dry_run=False, operations=None):
    result = []
    for pkg in packages:
        if dry_run:
            operations.append(f"install {pkg}")
        else:
            result.append(f"installed {pkg}")
    return result

def test_run_dry_run_true():
    pkgs = ["a", "b"]
    result, ops = install_packages(pkgs, dry_run=True)
    assert result == []
    assert ops == ["install a", "install b"]

def test_run_dry_run_false():
    pkgs = ["x"]
    res = install_packages(pkgs, dry_run=False)
    assert res == ["installed x"]
