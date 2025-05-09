import os
import json
import shutil

# Helper functions for version parsing and comparison
def parse_version(v):
    return tuple(int(x) for x in v.split('.'))

def compare_versions(v1, v2):
    t1 = parse_version(v1)
    t2 = parse_version(v2)
    # pad shorter
    length = max(len(t1), len(t2))
    t1 += (0,) * (length - len(t1))
    t2 += (0,) * (length - len(t2))
    if t1 < t2:
        return -1
    if t1 > t2:
        return 1
    return 0

def parse_spec(spec):
    """
    Parses a spec like "pkg>=1.0,<2.0" or "pkg==1.0"
    Returns (name, [(op, version), ...])
    """
    if '==' in spec:
        name, ver = spec.split('==', 1)
        return name, [('==', ver)]
    if '>=' in spec or '<=' in spec or '>' in spec or '<' in spec:
        parts = spec.split(None, 1)[0]
        # find first non-name char
        name = ''
        i = 0
        while i < len(spec) and spec[i].isalnum() or spec[i] in ['_','-']:
            name += spec[i]
            i += 1
        constraints = spec[len(name):]
        # split by comma
        cons = []
        for c in constraints.split(','):
            c = c.strip()
            if not c:
                continue
            op = None
            for o in ['>=', '<=', '==', '>', '<']:
                if c.startswith(o):
                    op = o
                    ver = c[len(o):]
                    break
            if not op:
                raise ValueError(f"Invalid constraint '{c}'")
            cons.append((op, ver))
        return name, cons
    # no constraint, any version
    return spec, []

def satisfies_constraints(version, constraints):
    for op, ver in constraints:
        cmp = compare_versions(version, ver)
        if op == '==' and cmp != 0:
            return False
        if op == '>=' and cmp < 0:
            return False
        if op == '<=' and cmp > 0:
            return False
        if op == '>' and cmp <= 0:
            return False
        if op == '<' and cmp >= 0:
            return False
    return True

def load_env_metadata(env_path):
    meta_file = os.path.join(env_path, 'env.json')
    if not os.path.exists(meta_file):
        raise ValueError(f"Environment at {env_path} not found")
    with open(meta_file, 'r') as f:
        return json.load(f)

def save_env_metadata(env_path, data):
    meta_file = os.path.join(env_path, 'env.json')
    with open(meta_file, 'w') as f:
        json.dump(data, f, indent=2)

def load_index(index_file):
    if not os.path.exists(index_file):
        raise ValueError(f"Index file {index_file} not found")
    with open(index_file, 'r') as f:
        return json.load(f)

def load_offline_packages(offline_dir):
    if not os.path.isdir(offline_dir):
        raise ValueError(f"Offline dir {offline_dir} not found")
    pkgs = []
    for fname in os.listdir(offline_dir):
        if not fname.endswith('.json'):
            continue
        path = os.path.join(offline_dir, fname)
        with open(path, 'r') as f:
            pkgs.append(json.load(f))
    return pkgs

def create_env(env_path):
    if os.path.exists(env_path):
        raise ValueError(f"Environment at {env_path} already exists")
    os.makedirs(env_path, exist_ok=False)
    data = {'packages': {}}
    save_env_metadata(env_path, data)

def install_packages(env_path, package_specs, offline_dir=None, index_file=None):
    """
    package_specs: list of spec strings
    """
    data = load_env_metadata(env_path)
    # load available packages
    if offline_dir:
        available = load_offline_packages(offline_dir)
    else:
        idx = index_file or 'index.json'
        available = load_index(idx)
    # map name -> list of package dicts
    pkg_map = {}
    for pkg in available:
        pkg_map.setdefault(pkg['name'], []).append(pkg)
    # recursive install
    visited = set()
    def _install(spec, parent=None):
        name, constraints = parse_spec(spec)
        if name in data['packages']:
            # already installed, check version satisfies
            inst_ver = data['packages'][name]['version']
            if not satisfies_constraints(inst_ver, constraints):
                raise ValueError(f"Version conflict for {name}: installed {inst_ver} doesn't satisfy {constraints}")
            return
        # find candidates
        candidates = pkg_map.get(name, [])
        # filter by constraints
        valid = [p for p in candidates if satisfies_constraints(p['version'], constraints)]
        if not valid:
            raise ValueError(f"No candidate found for {spec}")
        # pick highest version
        valid.sort(key=lambda p: parse_version(p['version']), reverse=True)
        chosen = valid[0]
        # mark installed to prevent cycles
        data['packages'][name] = {
            'version': chosen['version'],
            'dependencies': chosen.get('dependencies', {}),
            'installed_from': parent
        }
        # install dependencies
        for dep_name, dep_cons in chosen.get('dependencies', {}).items():
            _install(f"{dep_name}{dep_cons}", parent=name)
    for spec in package_specs:
        _install(spec, parent=None)
    save_env_metadata(env_path, data)

def generate_lockfile(env_path, lockfile_path):
    data = load_env_metadata(env_path)
    lines = []
    for name, info in sorted(data['packages'].items()):
        lines.append(f"{name}=={info['version']}")
    with open(lockfile_path, 'w') as f:
        f.write('\n'.join(lines))

def export_env(env_path, file_path):
    # same as lockfile
    generate_lockfile(env_path, file_path)

def import_env(env_path, lockfile_path, offline_dir=None, index_file=None):
    if not os.path.exists(lockfile_path):
        raise ValueError(f"Lockfile {lockfile_path} not found")
    with open(lockfile_path, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    create_env(env_path)
    install_packages(env_path, lines, offline_dir=offline_dir, index_file=index_file)

def check_package_installed(env_path, package_name):
    data = load_env_metadata(env_path)
    return package_name in data['packages']

def check_updates(env_path, index_file=None):
    data = load_env_metadata(env_path)
    idx = index_file or 'index.json'
    available = load_index(idx)
    latest_map = {}
    for pkg in available:
        name = pkg['name']
        ver = pkg['version']
        if name not in latest_map or compare_versions(ver, latest_map[name]) > 0:
            latest_map[name] = ver
    outdated = {}
    for name, info in data['packages'].items():
        inst = info['version']
        latest = latest_map.get(name)
        if latest and compare_versions(latest, inst) > 0:
            outdated[name] = {'current': inst, 'latest': latest}
    return outdated

def check_vulnerabilities(env_path, vulnerability_db_file=None):
    data = load_env_metadata(env_path)
    db_file = vulnerability_db_file or os.path.join(os.path.dirname(__file__), 'vulnerability_db.json')
    if not os.path.exists(db_file):
        raise ValueError(f"Vulnerability DB {db_file} not found")
    with open(db_file, 'r') as f:
        db = json.load(f)
    alerts = {}
    for name, info in data['packages'].items():
        vulns = db.get(name, [])
        if info['version'] in vulns:
            alerts[name] = info['version']
    return alerts

def dependency_explanation(env_path, package_name):
    data = load_env_metadata(env_path)
    if package_name not in data['packages']:
        raise ValueError(f"{package_name} not installed")
    # build tree
    def _explain(name, level=0, seen=None):
        if seen is None:
            seen = set()
        indent = '  ' * level
        info = data['packages'][name]
        line = f"{indent}{name}=={info['version']}"
        lines = [line]
        deps = info.get('dependencies', {})
        for dep_name in deps:
            if dep_name in seen:
                lines.append(f"{indent}  {dep_name} (circular)")
            else:
                seen2 = seen | {name}
                lines.extend(_explain(dep_name, level+1, seen2))
        return lines
    return '\n'.join(_explain(package_name))
