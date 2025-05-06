import os
import shutil
from utils import (
    parse_version, compare_versions, parse_constraints,
    satisfies_constraints, load_json, save_json, read_lines, write_lines
)

def load_env_metadata(env_path):
    path = os.path.join(env_path, "env.json")
    return load_json(path)

def save_env_metadata(env_path, data):
    path = os.path.join(env_path, "env.json")
    save_json(path, data)

def load_index(index_file):
    return load_json(index_file)

def load_offline_packages(offline_dir):
    if not os.path.isdir(offline_dir):
        raise ValueError(f"Offline dir {offline_dir} not found")
    pkgs = []
    for fname in os.listdir(offline_dir):
        if not fname.endswith(".json"):
            continue
        pkgs.append(load_json(os.path.join(offline_dir, fname)))
    return pkgs

def create_env(env_path):
    if os.path.exists(env_path):
        raise ValueError(f"Environment at {env_path} already exists")
    os.makedirs(env_path, exist_ok=False)
    data = {"packages": {}}
    save_env_metadata(env_path, data)

def install_recursive(spec, data_packages, pkg_map, parent=None):
    name, constraints = parse_constraints(spec)
    # already installed?
    if name in data_packages:
        inst = data_packages[name]["version"]
        if not satisfies_constraints(inst, constraints):
            raise ValueError(f"Version conflict for {name}: installed {inst} doesn't satisfy {constraints}")
        return
    # find candidates
    candidates = pkg_map.get(name, [])
    valid = [p for p in candidates if satisfies_constraints(p["version"], constraints)]
    if not valid:
        raise ValueError(f"No candidate found for {spec}")
    # choose highest
    valid.sort(key=lambda p: parse_version(p["version"]), reverse=True)
    chosen = valid[0]
    data_packages[name] = {
        "version": chosen["version"],
        "dependencies": chosen.get("dependencies", {}),
        "installed_from": parent
    }
    # recurse on dependencies
    for dep_name, dep_cons in chosen.get("dependencies", {}).items():
        install_recursive(f"{dep_name}{dep_cons}", data_packages, pkg_map, parent=name)

def install_packages(env_path, package_specs, offline_dir=None, index_file=None):
    data = load_env_metadata(env_path)
    if offline_dir:
        available = load_offline_packages(offline_dir)
    else:
        idx = index_file or "index.json"
        available = load_index(idx)
    pkg_map = {}
    for pkg in available:
        pkg_map.setdefault(pkg["name"], []).append(pkg)
    for spec in package_specs:
        install_recursive(spec, data["packages"], pkg_map, parent=None)
    save_env_metadata(env_path, data)

def generate_lockfile(env_path, lockfile_path):
    data = load_env_metadata(env_path)
    lines = [f"{n}=={info['version']}" for n, info in sorted(data["packages"].items())]
    write_lines(lockfile_path, lines)

def export_env(env_path, file_path):
    generate_lockfile(env_path, file_path)

def import_env(env_path, lockfile_path, offline_dir=None, index_file=None):
    if not os.path.exists(lockfile_path):
        raise ValueError(f"Lockfile {lockfile_path} not found")
    lines = [l for l in read_lines(lockfile_path) if l and not l.startswith("#")]
    create_env(env_path)
    install_packages(env_path, lines, offline_dir=offline_dir, index_file=index_file)

def check_package_installed(env_path, package_name):
    data = load_env_metadata(env_path)
    return package_name in data["packages"]

def check_updates(env_path, index_file=None):
    data = load_env_metadata(env_path)
    idx = index_file or "index.json"
    available = load_index(idx)
    latest = {}
    for pkg in available:
        n, v = pkg["name"], pkg["version"]
        if n not in latest or compare_versions(v, latest[n]) > 0:
            latest[n] = v
    outdated = {}
    for n, info in data["packages"].items():
        cur = info["version"]
        if n in latest and compare_versions(latest[n], cur) > 0:
            outdated[n] = {"current": cur, "latest": latest[n]}
    return outdated

def check_vulnerabilities(env_path, vulnerability_db_file=None):
    data = load_env_metadata(env_path)
    dbf = vulnerability_db_file or os.path.join(os.path.dirname(__file__), 'vulnerability_db.json')
    db = load_json(dbf)
    alerts = {}
    for n, info in data["packages"].items():
        if info["version"] in db.get(n, []):
            alerts[n] = info["version"]
    return alerts

def dependency_explanation(env_path, package_name):
    data = load_env_metadata(env_path)
    if package_name not in data["packages"]:
        raise ValueError(f"{package_name} not installed")
    def _explain(name, level=0, seen=None):
        seen = seen or set()
        indent = "  " * level
        info = data["packages"][name]
        lines = [f"{indent}{name}=={info['version']}"]
        for dep in info.get("dependencies", {}):
            if dep in seen:
                lines.append(f"{indent}  {dep} (circular)")
            else:
                lines += _explain(dep, level+1, seen | {name})
        return lines
    return "\n".join(_explain(package_name))
