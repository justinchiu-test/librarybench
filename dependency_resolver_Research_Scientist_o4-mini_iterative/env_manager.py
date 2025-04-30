import os
import sys
import json
import shutil
import tarfile
import re
from glob import glob
from datetime import datetime
import click

# Version parsing and comparison
def parse_version(v):
    return tuple(int(x) for x in v.split('.'))

def version_satisfies(v, constraint):
    # constraint like ">=1.0", "==2.0"
    m = re.match(r'(>=|==)(.+)', constraint)
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
ROOT = os.getenv('ENV_MANAGER_ROOT', os.path.join(os.getcwd(), '.env_manager'))
REPOS_FILE = os.path.join(ROOT, 'repos.json')
CACHE_DIR = os.path.join(ROOT, 'cache')
ENVS_DIR = os.path.join(ROOT, 'envs')
SNAPSHOTS_DIR = os.path.join(ROOT, 'snapshots')
CURRENT_ENV_FILE = os.path.join(ROOT, 'current_env')

def ensure_dirs():
    for d in [ROOT, CACHE_DIR, ENVS_DIR, SNAPSHOTS_DIR]:
        os.makedirs(d, exist_ok=True)
    if not os.path.exists(REPOS_FILE):
        with open(REPOS_FILE, 'w') as f:
            json.dump([], f)

class RepoManager:
    def __init__(self):
        ensure_dirs()
        self.repos = self._load()

    def _load(self):
        with open(REPOS_FILE, 'r') as f:
            return json.load(f)

    def _save(self):
        with open(REPOS_FILE, 'w') as f:
            json.dump(self.repos, f, indent=2)

    def add(self, name, url):
        if any(r['name']==name for r in self.repos):
            raise click.ClickException(f"Repo '{name}' already exists")
        self.repos.append({'name': name, 'url': url})
        self._save()

    def list(self):
        return self.repos

class CacheManager:
    def __init__(self):
        ensure_dirs()
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
        ensure_dirs()
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
        os.makedirs(os.path.join(path, 'packages'), exist_ok=True)
        with open(self._installed_file(name), 'w') as f:
            json.dump([], f)

    def list(self):
        return [d for d in os.listdir(ENVS_DIR)
                if os.path.isdir(self._env_path(d))]

    def switch(self, name):
        if name not in self.list():
            raise click.ClickException(f"Env '{name}' does not exist")
        with open(CURRENT_ENV_FILE, 'w') as f:
            f.write(name)

    def current(self):
        if not os.path.exists(CURRENT_ENV_FILE):
            return None
        with open(CURRENT_ENV_FILE, 'r') as f:
            return f.read().strip()

    def list_installed(self, env):
        with open(self._installed_file(env), 'r') as f:
            return json.load(f)

    def show_metadata(self, env, pkg_name):
        inst = self.list_installed(env)
        rec = next((p for p in inst if p['name']==pkg_name), None)
        if not rec:
            raise click.ClickException(f"Package '{pkg_name}' not installed")
        pkg_dir = os.path.join(self._env_path(env), 'packages',
                               f"{pkg_name}-{rec['version']}")
        meta_f = os.path.join(pkg_dir, 'metadata.json')
        with open(meta_f) as f:
            return json.load(f)

    def _snapshot(self, env):
        snaps_env_dir = os.path.join(SNAPSHOTS_DIR, env)
        os.makedirs(snaps_env_dir, exist_ok=True)
        existing = os.listdir(snaps_env_dir)
        idx = max([int(n) for n in existing if n.isdigit()] or [0]) + 1
        dst = os.path.join(snaps_env_dir, str(idx))
        shutil.copytree(self._env_path(env), dst)
        return idx

    def rollback(self, env):
        snaps_env_dir = os.path.join(SNAPSHOTS_DIR, env)
        if not os.path.isdir(snaps_env_dir):
            raise click.ClickException("No snapshots to rollback")
        snaps = [n for n in os.listdir(snaps_env_dir) if n.isdigit()]
        if not snaps:
            raise click.ClickException("No snapshots to rollback")
        last = max(int(n) for n in snaps)
        src = os.path.join(snaps_env_dir, str(last))
        dst = self._env_path(env)
        shutil.rmtree(dst)
        shutil.copytree(src, dst)

    def _find_packages(self, name, constraint=None):
        # search repos for matching packages
        candidates = []
        for repo in self.repo_mgr.list():
            url = repo['url']
            if not os.path.isdir(url):
                continue
            for fn in os.listdir(url):
                m = re.match(rf'^{re.escape(name)}-([\d\.]+)\.tar\.gz$', fn)
                if m:
                    ver = m.group(1)
                    if constraint and not version_satisfies(ver, constraint):
                        continue
                    candidates.append((parse_version(ver), ver, os.path.join(url, fn)))
        if not candidates:
            return None
        # pick highest
        _, ver, path = sorted(candidates)[-1]
        return {'name': name, 'version': ver, 'path': path}

    def _read_metadata_from_tar(self, tar_path):
        with tarfile.open(tar_path, 'r:gz') as tf:
            try:
                m = tf.extractfile('metadata.json')
                return json.load(m)
            except KeyError:
                raise click.ClickException("metadata.json missing in package")

    def install(self, env, reqs, offline=False):
        if env not in self.list():
            raise click.ClickException(f"Env '{env}' does not exist")
        # snapshot
        self._snapshot(env)
        installed = self.list_installed(env)

        def _install_one(req):
            # parse requirement
            m = re.match(r'^([^=<>]+?)(?:(>=|==)(.+))?$', req)
            if not m:
                raise click.ClickException(f"Invalid requirement '{req}'")
            pkg_name = m.group(1)
            if m.group(2):
                constraint = m.group(2) + m.group(3)
            else:
                constraint = None

            # find package info
            if offline:
                # search in cache
                candidates = []
                for fn in os.listdir(self.cache_mgr.cache):
                    m2 = re.match(rf'^{re.escape(pkg_name)}-([\d\.]+)\.tar\.gz$', fn)
                    if m2:
                        ver = m2.group(1)
                        if constraint and not version_satisfies(ver, constraint):
                            continue
                        candidates.append((parse_version(ver), ver, os.path.join(self.cache_mgr.cache, fn)))
                if not candidates:
                    raise click.ClickException(f"Package '{req}' not found in cache")
                _, ver, path = sorted(candidates)[-1]
                info = {'name': pkg_name, 'version': ver, 'path': path}
            else:
                info = self._find_packages(pkg_name, constraint)
                if not info:
                    raise click.ClickException(f"Package '{req}' not found in repos")
                ver, path = info['version'], info['path']

            name2, ver2, path2 = info['name'], info['version'], info['path']
            # skip if already installed
            if any(p['name']==name2 and p['version']==ver2 for p in installed):
                return

            # read metadata
            meta = self._read_metadata_from_tar(path2)
            # install dependencies first
            for dep in meta.get('dependencies', []):
                _install_one(dep)

            # get package archive path
            if offline:
                pkg_path = path2
            else:
                pkg_path = self.cache_mgr.add(path2, name2, ver2)

            # extract into environment
            pkg_dir = os.path.join(self._env_path(env), 'packages', f"{name2}-{ver2}")
            os.makedirs(pkg_dir, exist_ok=True)
            with tarfile.open(pkg_path, 'r:gz') as tf:
                tf.extractall(pkg_dir)

            # record installation
            installed.append({'name': name2, 'version': ver2})
            with open(self._installed_file(env), 'w') as f:
                json.dump(installed, f, indent=2)

        # install each requested package
        for req in reqs:
            _install_one(req)

    def uninstall(self, env, names):
        if env not in self.list():
            raise click.ClickException(f"Env '{env}' does not exist")
        installed = self.list_installed(env)
        remaining = [p for p in installed if p['name'] not in names]
        # remove package dirs
        for p in installed:
            if p['name'] in names:
                pkg_dir = os.path.join(self._env_path(env), 'packages',
                                       f"{p['name']}-{p['version']}")
                if os.path.isdir(pkg_dir):
                    shutil.rmtree(pkg_dir)
        with open(self._installed_file(env), 'w') as f:
            json.dump(remaining, f, indent=2)

    def lock(self, env, lockfile):
        data = {'env': env, 'packages': self.list_installed(env)}
        with open(lockfile, 'w') as f:
            json.dump(data, f, indent=2)

    def install_lockfile(self, lockfile, env):
        if env in self.list():
            raise click.ClickException(f"Env '{env}' already exists")
        with open(lockfile) as f:
            data = json.load(f)
        pkgs = data['packages']
        self.create(env)
        # install each exact pkg
        for p in pkgs:
            name, ver = p['name'], p['version']
            # find tar in cache or repo
            path = self.cache_mgr.get(name, ver)
            if not path:
                info = self._find_packages(name, f"=={ver}")
                if not info:
                    raise click.ClickException(f"Package '{name}-{ver}' not found")
                path = self.cache_mgr.add(info['path'], name, ver)
            # extract
            pkg_dir = os.path.join(self._env_path(env), 'packages', f"{name}-{ver}")
            os.makedirs(pkg_dir, exist_ok=True)
            with tarfile.open(path, 'r:gz') as tf:
                tf.extractall(pkg_dir)
        # write installed.json
        with open(self._installed_file(env), 'w') as f:
            json.dump(pkgs, f, indent=2)

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
    for e in em.list():
        current = em.current()
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
