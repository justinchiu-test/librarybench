import os
from utils import (
    parse_version, compare_versions,
    parse_spec_multi, satisfies_constraints,
    load_json_file, save_json_file
)

# -- helper for recursive install --

def install_recursive(data, pkg_map, spec, parent=None):
    name, constraints = parse_spec_multi(spec)
    # check already installed
    if name in data['packages']:
        inst_ver = data['packages'][name]['version']
        if not satisfies_constraints(inst_ver, constraints):
            raise ValueError(
                f"Version conflict for {name}: installed {inst_ver} "
                f"doesn't satisfy {constraints}"
            )
        return
    # candidates
    candidates = pkg_map.get(name, [])
    valid = [p for p in candidates if satisfies_constraints(p['version'], constraints)]
    if not valid:
        raise ValueError(f"No candidate found for {spec}")
    valid.sort(key=lambda p: parse_version(p['version']), reverse=True)
    chosen = valid[0]
    data['packages'][name] = {
        'version': chosen['version'],
        'dependencies': chosen.get('dependencies', {}),
        'installed_from': parent
    }
    # install dependencies
    for dep_name, dep_cons in chosen.get('dependencies', {}).items():
        install_recursive(data, pkg_map, f"{dep_name}{dep_cons}", parent=name)

def load_env_metadata(env_path):
    meta_file = os.path.join(env_path, 'env.json')
    return load_json_file(meta_file)

def save_env_metadata(env_path, data):
    meta_file = os.path.join(env_path, 'env.json')
    save_json_file(meta_file, data)

def load_index(index_file):
    return load_json_file(index_file)

def load_offline_packages(offline_dir):
    if not os.path.isdir(offline_dir):
        raise ValueError(f"Offline dir {offline_dir} not found")
    pkgs = []
    for fname in os.listdir(offline_dir):
        if not fname.endswith('.json'):
            continue
        pkgs.append(load_json_file(os.path.join(offline_dir, fname)))
    return pkgs

def create_env(env_path):
    if os.path.exists(env_path):
        raise ValueError(f"Environment at {env_path} already exists")
    os.makedirs(env_path, exist_ok=False)
    save_env_metadata(env_path, {'packages': {}})

def install_packages(env_path, package_specs, offline_dir=None, index_file=None):
    data = load_env_metadata(env_path)
    if offline_dir:
        available = load_offline_packages(offline_dir)
    else:
        idx = index_file or 'index.json'
        available = load_index(idx)
    pkg_map = {}
    for pkg in available:
        pkg_map.setdefault(pkg['name'], []).append(pkg)
    for spec in package_specs:
        install_recursive(data, pkg_map, spec, parent=None)
    save_env_metadata(env_path, data)

def generate_lockfile(env_path, lockfile_path):
    data = load_env_metadata(env_path)
    lines = [f"{n}=={info['version']}" for n, info in sorted(data['packages'].items())]
    with open(lockfile_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

def export_env(env_path, file_path):
    generate_lockfile(env_path, file_path)

def import_env(env_path, lockfile_path, offline_dir=None, index_file=None):
    if not os.path.exists(lockfile_path):
        raise ValueError(f"Lockfile {lockfile_path} not found")
    with open(lockfile_path, 'r', encoding='utf-8') as f:
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
    vulndb = load_json_file(db_file)
    alerts = {}
    for name, info in data['packages'].items():
        if info['version'] in vulndb.get(name, []):
            alerts[name] = info['version']
    return alerts

def dependency_explanation(env_path, package_name):
    data = load_env_metadata(env_path)
    if package_name not in data['packages']:
        raise ValueError(f"{package_name} not installed")
    def _explain(name, level=0, seen=None):
        seen = seen or set()
        indent = '  ' * level
        info = data['packages'][name]
        lines = [f"{indent}{name}=={info['version']}"]
        for dep in info.get('dependencies', {}):
            if dep in seen:
                lines.append(f"{indent}  {dep} (circular)")
            else:
                lines.extend(_explain(dep, level+1, seen | {name}))
        return lines
    return '\n'.join(_explain(package_name))
