import re

def parse_version(version):
    """
    Parse semantic version strings in the form 'major.minor.patch'.
    Missing minor or patch parts are treated as zero.
    Returns a tuple of ints: (major, minor, patch).
    Raises ValueError on invalid strings.
    """
    parts = version.split('.')
    # pad to length 3
    parts = (parts + ['0', '0', '0'])[:3]
    try:
        return tuple(int(p) for p in parts)
    except Exception:
        raise ValueError(f"Invalid version string: {version}")

def ensure_backward_compatibility(current_version, previous_version):
    """
    Ensure the current version is backward compatible with the previous version.
    Under semantic versioning, backward compatibility requires:
      - The same major version.
      - The current minor version >= previous minor version.
      - If minors are equal, current patch version >= previous patch version.
    Returns True if compatible, False otherwise.
    """
    cur_major, cur_minor, cur_patch = parse_version(current_version)
    prev_major, prev_minor, prev_patch = parse_version(previous_version)

    # Major version must match
    if cur_major != prev_major:
        return False
    # Minor must not be less than previous
    if cur_minor < prev_minor:
        return False
    # If minor equal, patch must not be less than previous
    if cur_minor == prev_minor and cur_patch < prev_patch:
        return False
    return True

def run_integration_tests(test_suite):
    """
    Runs an integration test suite provided as a mapping:
      { test_name (str): test_callable () -> bool-like or raises Exception }
    For each test:
      - If it returns a truthy value, it's considered a pass.
      - If it returns a falsey value, it's considered a fail (no error message).
      - If it raises an exception, it's considered a fail with the exception message.
    Returns a dict:
      {
        test_name: {
          'success': bool,
          'error': str or None
        },
        ...
      }
    """
    results = {}
    for name, test in test_suite.items():
        try:
            outcome = test()
            success = bool(outcome)
            results[name] = {
                'success': success,
                'error': None
            }
        except Exception as e:
            results[name] = {
                'success': False,
                'error': str(e)
            }
    return results
