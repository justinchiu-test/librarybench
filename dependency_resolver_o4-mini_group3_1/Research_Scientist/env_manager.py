import os
import re
import shutil
import tarfile
import click
from glob import glob
from datetime import datetime
from utils import (
    read_json, write_json, ensure_dirs, list_dirs,
    remove_tree, copy_tree, extract_tar,
    parse_requirement, find_tar_candidates, pick_highest
)

# Version parsing and comparison
def parse_version(v):
    return tuple(int(x) for x in v.split('.'))

def version_satisfies(v, constraint):
    m = re.match(r'(>=|==)(.+)', constraint or '')
    if not m:
        return False
    op, ver = m.group(1), m.group(2)
    v_t, ver_t = parse_version(v), parse_version(ver)
    if op == '==':
        return v_t == ver_t
    if op == '>=':
        return v_t >= ver_t
    return False

# Configuration root
ROOT = os.getenv('ENV_MANAGER_ROOT',
                 os.path.join(os.getcwd(), '.env_manager'))
REPOS_FILE = os.path.join(ROOT, 'repos.json')
CACHE_DIR = os.path.join(ROOT, 'cache')
ENVS_DIR = os.path.join(ROOT, 'envs')
SNAPSHOTS_DIR = os.path.join(ROOT, 'snapshots')
CURRENT_ENV_FILE = os.path.join(ROOT, 'current_env')

def ensure_dirs_all():
    ensure_dirs(ROOT, CACHE_DIR, ENVS_DIR, SNAPSHOTS_DIR)
    if not os.path.exists(REPOS_FILE):
        write_json(REPOS_FILE, [])

class RepoManager:
    def __init__(self):
        ensure_dirs_all()
        self.repos = self._load()

    def _load(self):
        return read_json(REPOS_FILE)

    def _save(self):
        write_json(REPOS_FILE, self.repos, indent=2)

    def add(self, name, url):
        if any(r['name'] == name for r in self.repos):
            raise click.ClickException(f"Repo '{name}' already exists")
        self.repos.append({'name': name, 'url': url})
        self._save()

    def list(self):
        return self.repos

class CacheManager:
    def __init__(self):
        ensure_dirs_all()
        self.cache = CACHE_DIR

    def has(self, name, version):
        path = os.path.join(self.cache, f"{name}-{version}.tar.gz")
        return os.path.exists(path)

    def add(self, src_path, name, version):
        dst = os.path.join(self.cache, f"{name}-{version}.tar.gz")
        if not os.path.exists(dst):
            shutil.copy2(src_path, dst)
        return dst

    def get(self, name, version):
        path = os.path.join(self.cache, f"{name}-{version}.tar.gz")
        return path if os.path.exists(path) else None

class EnvManager:
    def __init__(self, repo_mgr, cache_mgr):
        ensure_dirs_all()
        self.repo_mgr = repo_mgr
        self.cache_mgr = cache_mgr

    def _env_path(self, name):
        return os.path.join(ENVS_DIR, name)

    def _installed_file(self, name):
        return os.path.join(self._env_path(name), 'installed.json')

    def create(self, name):
        path = self._env_path(name)
        if os.path.exists(path):
            raise click.ClickException(f"Env '{name}' already exists")
        ensure_dirs(os.path.join(path, 'packages'))
        write_json(self._installed_file(name), [])

    def list(self):
        return list_dirs(ENVS_DIR)

    def switch(self, name):
        if name not in self.list():
            raise click.ClickException(f"Env '{name}' does not exist")
        with open(CURRENT_ENV_FILE, 'w') as f:
            f.write(name)

    def current(self):
        if not os.path.exists(CURRENT_ENV_FILE):
            return None
        return open(CURRENT_ENV_FILE).read().strip()

    def list_installed(self, env):
        return read_json(self._installed_file(env))

    def show_metadata(self, env, pkg_name):
        installed = self.list_installed(env)
        rec = next((p for p in installed if p['name'] == pkg_name), None)
        if not rec:
            raise click.ClickException(
                f"Package '{pkg_name}' not installed")
        pkg_dir = os.path.join(
            self._env_path(env), 'packages',
            f"{pkg_name}-{rec['version']}"
        )
        meta_f = os.path.join(pkg_dir, 'metadata.json')
        return read_json(meta_f)

    def _snapshot(self, env):
        snaps_env = os.path.join(SNAPSHOTS_DIR, env)
        ensure_dirs(snaps_env)
        existing = [n for n in os.listdir(snaps_env) if n.isdigit()]
        idx = max([int(n) for n in existing] or [0]) + 1
        dst = os.path.join(snaps_env, str(idx))
        copy_tree(self._env_path(env), dst)
        return idx

    def rollback(self, env):
        snaps_env = os.path.join(SNAPSHOTS_DIR, env)
        snaps = [n for n in os.listdir(snaps_env)
                 if os.path.isdir(os.path.join(snaps_env, n)) and n.isdigit()]
        if not snaps:
            raise click.ClickException("No snapshots to rollback")
        last = max(int(n) for n in snaps)
        src = os.path.join(snaps_env, str(last))
        dst = self._env_path(env)
        remove_tree(dst)
        copy_tree(src, dst)

    def _find_packages(self, name, constraint=None):
        candidates = []
        for repo in self.repo_mgr.list():
            url = repo['url']
            if not os.path.isdir(url):
                continue
            c = find_tar_candidates(
                url, name, constraint, version_satisfies)
            for ver, path in c:
                candidates.append((ver, path))
        ver, path = pick_highest(candidates, parse_version)
        if not path:
            return None
        return {'name': name, 'version': ver, 'path': path}

    def _read_metadata_from_tar(self, tar_path):
        with tarfile.open(tar_path, 'r:gz') as tf:
            try:
                m = tf.extractfile('metadata.json')
                return json.load(m)
            except KeyError:
                raise click.ClickException(
                    "metadata.json missing in package")

    def _install_one(self, env, req, installed, offline):
        name, constraint = parse_requirement(req)
        if not name:
            raise click.ClickException(f"Invalid requirement '{req}'")
        # locate package
        if offline:
            c = find_tar_candidates(
                self.cache_mgr.cache, name, constraint, version_satisfies)
            ver, path = pick_highest(c, parse_version)
            if not path:
                raise click.ClickException(
                    f"Package '{req}' not found in cache")
        else:
            info = self._find_packages(name, constraint)
            if not info:
                raise click.ClickException(
                    f"Package '{req}' not found in repos")
            ver, path = info['version'], info['path']
        # skip if already installed exact
        if any(p['name'] == name and p['version'] == ver
               for p in installed):
            return
        meta = self._read_metadata_from_tar(path)
        # dependencies
        for dep in meta.get('dependencies', []):
            self._install_one(env, dep, installed, offline)
        # cache if online
        pkg_path = path if offline else self.cache_mgr.add(path, name, ver)
        # extract
        pkg_dir = os.path.join(
            self._env_path(env), 'packages', f"{name}-{ver}")
        ensure_dirs(pkg_dir)
        extract_tar(pkg_path, pkg_dir)
        # record
        installed.append({'name': name, 'version': ver})
        write_json(self._installed_file(env), installed, indent=2)

    def install(self, env, reqs, offline=False):
        if env not in self.list():
            raise click.ClickException(f"Env '{env}' does not exist")
        # snapshot and load state
        self._snapshot(env)
        installed = self.list_installed(env)
        for req in reqs:
            self._install_one(env, req, installed, offline)

    def uninstall(self, env, names):
        if env not in self.list():
            raise click.ClickException(f"Env '{env}' does not exist")
        installed = self.list_installed(env)
        remaining = [p for p in installed if p['name'] not in names]
        for p in installed:
            if p['name'] in names:
                pkg_dir = os.path.join(
                    self._env_path(env), 'packages',
                    f"{p['name']}-{p['version']}")
                remove_tree(pkg_dir)
        write_json(self._installed_file(env), remaining, indent=2)

    def lock(self, env, lockfile):
        data = {'env': env, 'packages': self.list_installed(env)}
        write_json(lockfile, data, indent=2)

    def install_lockfile(self, lockfile, env):
        if env in self.list():
            raise click.ClickException(f"Env '{env}' already exists")
        data = read_json(lockfile)
        self.create(env)
        for p in data['packages']:
            name, ver = p['name'], p['version']
            path = self.cache_mgr.get(name, ver)
            if not path:
                info = self._find_packages(name, f"=={ver}")
                if not info:
                    raise click.ClickException(
                        f"Package '{name}-{ver}' not found")
                path = self.cache_mgr.add(info['path'], name, ver)
            pkg_dir = os.path.join(
                self._env_path(env), 'packages', f"{name}-{ver}")
            ensure_dirs(pkg_dir)
            extract_tar(path, pkg_dir)
        write_json(self._installed_file(env), data['packages'], indent=2)

# CLI
@click.group()
def main():
    """Env Manager CLI"""
    pass

@main.group()
def repo():
    "Manage repositories"
    pass

@repo.command('add')
@click.argument('name')
@click.argument('url')
def repo_add(name, url):
    rm = RepoManager()
    rm.add(name, url)
    click.echo(f"Added repo '{name}' -> {url}")

@repo.command('list')
def repo_list():
    rm = RepoManager()
    for r in rm.list():
        click.echo(f"{r['name']}: {r['url']}")

@main.group()
def env():
    "Manage environments"
    pass

@env.command('create')
@click.argument('name')
def env_create(name):
    em = EnvManager(RepoManager(), CacheManager())
    em.create(name)
    click.echo(f"Created env '{name}'")

@env.command('list')
def env_list():
    em = EnvManager(RepoManager(), CacheManager())
    current = em.current()
    for e in em.list():
        mark = '*' if e == current else ' '
        click.echo(f"{mark} {e}")

@env.command('switch')
@click.argument('name')
def env_switch(name):
    em = EnvManager(RepoManager(), CacheManager())
    em.switch(name)
    click.echo(f"Switched to env '{name}'")

@main.command('install')
@click.argument('packages', nargs=-1)
@click.option('-e', '--env', 'env_name', required=False)
@click.option('--offline', is_flag=True, default=False)
def install(packages, env_name, offline):
    if not packages:
        raise click.ClickException("No packages specified")
    em = EnvManager(RepoManager(), CacheManager())
    env_name = env_name or em.current()
    if not env_name:
        raise click.ClickException("No environment specified")
    em.install(env_name, list(packages), offline=offline)
    click.echo(f"Installed {', '.join(packages)} into '{env_name}'")

@main.command('uninstall')
@click.argument('packages', nargs=-1)
@click.option('-e', '--env', 'env_name', required=False)
def uninstall(packages, env_name):
    if not packages:
        raise click.ClickException("No packages specified")
    em = EnvManager(RepoManager(), CacheManager())
    env_name = env_name or em.current()
    if not env_name:
        raise click.ClickException("No environment specified")
    em.uninstall(env_name, list(packages))
    click.echo(f"Uninstalled {', '.join(packages)} from '{env_name}'")

@main.command('list')
@click.option('-e', '--env', 'env_name', required=False)
def list_pkgs(env_name):
    em = EnvManager(RepoManager(), CacheManager())
    env_name = env_name or em.current()
    if not env_name:
        raise click.ClickException("No environment specified")
    for p in em.list_installed(env_name):
        click.echo(f"{p['name']}=={p['version']}")

@main.command('show')
@click.argument('package')
@click.option('-e', '--env', 'env_name', required=False)
def show(package, env_name):
    em = EnvManager(RepoManager(), CacheManager())
    env = env_name or em.current()
    if not env:
        raise click.ClickException("No environment specified")
    meta = em.show_metadata(env, package)
    click.echo(json.dumps(meta, indent=2))

@main.command('rollback')
@click.option('-e', '--env', 'env_name', required=False)
def rollback(env_name):
    em = EnvManager(RepoManager(), CacheManager())
    env = env_name or em.current()
    if not env:
        raise click.ClickException("No environment specified")
    em.rollback(env)
    click.echo(f"Rolled back '{env}' to last snapshot")

@main.command('lock')
@click.argument('lockfile', type=click.Path())
@click.option('-e', '--env', 'env_name', required=False)
def lock(lockfile, env_name):
    em = EnvManager(RepoManager(), CacheManager())
    env = env_name or em.current()
    if not env:
        raise click.ClickException("No environment specified")
    em.lock(env, lockfile)
    click.echo(f"Lockfile written to {lockfile}")

@main.command('install-lockfile')
@click.argument('lockfile', type=click.Path())
@click.argument('env')
def install_lockfile(lockfile, env):
    em = EnvManager(RepoManager(), CacheManager())
    em.install_lockfile(lockfile, env)
    click.echo(f"Installed env '{env}' from lockfile")

if __name__ == '__main__':
    main()
