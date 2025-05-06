import os
import json
import shutil
import tarfile
import re
from glob import glob
from datetime import datetime
import click
from utils import (
    ensure_dirs, read_json, write_json, copy_tree, remove_path,
    get_next_index, parse_version, version_satisfies,
    find_latest_tar, extract_tar, parse_requirement
)

# Configuration root
ROOT = os.getenv('ENV_MANAGER_ROOT', os.path.join(os.getcwd(), '.env_manager'))
REPOS_FILE = os.path.join(ROOT, 'repos.json')
CACHE_DIR = os.path.join(ROOT, 'cache')
ENVS_DIR = os.path.join(ROOT, 'envs')
SNAPSHOTS_DIR = os.path.join(ROOT, 'snapshots')
CURRENT_ENV_FILE = os.path.join(ROOT, 'current_env')

def ensure_base_dirs():
    ensure_dirs([ROOT, CACHE_DIR, ENVS_DIR, SNAPSHOTS_DIR])
    if not os.path.exists(REPOS_FILE):
        write_json([], REPOS_FILE)

class RepoManager:
    def __init__(self):
        ensure_base_dirs()
        self.repos = self._load()

    def _load(self):
        return read_json(REPOS_FILE)

    def _save(self):
        write_json(self.repos, REPOS_FILE)

    def add(self, name, url):
        if any(r['name']==name for r in self.repos):
            raise click.ClickException(f"Repo '{name}' already exists")
        self.repos.append({'name': name, 'url': url})
        self._save()

    def list(self):
        return self.repos

class CacheManager:
    def __init__(self):
        ensure_base_dirs()
        self.cache = CACHE_DIR

    def has(self, name, version):
        return os.path.exists(os.path.join(self.cache, f"{name}-{version}.tar.gz"))

    def add(self, src_path, name, version):
        dst = os.path.join(self.cache, f"{name}-{version}.tar.gz")
        if not os.path.exists(dst):
            shutil.copy2(src_path, dst)
        return dst

    def get(self, name, version):
        p = os.path.join(self.cache, f"{name}-{version}.tar.gz")
        return p if os.path.exists(p) else None

class EnvManager:
    def __init__(self, repo_mgr, cache_mgr):
        ensure_base_dirs()
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
        ensure_dirs([os.path.join(path, 'packages')])
        write_json([], self._installed_file(name))

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
        return open(CURRENT_ENV_FILE).read().strip()

    def list_installed(self, env):
        return read_json(self._installed_file(env))

    def show_metadata(self, env, pkg_name):
        inst = self.list_installed(env)
        rec = next((p for p in inst if p['name']==pkg_name), None)
        if not rec:
            raise click.ClickException(f"Package '{pkg_name}' not installed")
        meta_f = os.path.join(self._env_path(env), 'packages',
                               f"{pkg_name}-{rec['version']}", 'metadata.json')
        return read_json(meta_f)

    def _snapshot(self, env):
        d = os.path.join(SNAPSHOTS_DIR, env)
        ensure_dirs([d])
        idx = get_next_index(d)
        dst = os.path.join(d, str(idx))
        copy_tree(self._env_path(env), dst)
        return idx

    def rollback(self, env):
        d = os.path.join(SNAPSHOTS_DIR, env)
        snaps = list_numeric_dirs(d) if os.path.isdir(d) else []
        if not snaps:
            raise click.ClickException("No snapshots to rollback")
        last = max(int(n) for n in snaps)
        src = os.path.join(d, str(last))
        dst = self._env_path(env)
        remove_path(dst)
        copy_tree(src, dst)

    def _find_packages(self, name, constraint=None):
        candidates = []
        for repo in self.repo_mgr.list():
            url = repo['url']
            if not os.path.isdir(url):
                continue
            info = find_latest_tar(url, name, constraint)
            if info:
                candidates.append((parse_version(info['version']),
                                   info['version'], info['path']))
        if not candidates:
            return None
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
        self._snapshot(env)
        installed = self.list_installed(env)

        def install_one(req):
            pkg_name, constraint = parse_requirement(req)
            if not pkg_name:
                raise click.ClickException(f"Invalid requirement '{req}'")
            if offline:
                info = find_latest_tar(self.cache_mgr.cache, pkg_name, constraint)
                if not info:
                    raise click.ClickException(f"Package '{req}' not found in cache")
            else:
                info = self._find_packages(pkg_name, constraint)
                if not info:
                    raise click.ClickException(f"Package '{req}' not found in repos")
            name2, ver2, path2 = info['name'], info['version'], info['path']
            if any(p['name']==name2 and p['version']==ver2 for p in installed):
                return
            meta = self._read_metadata_from_tar(path2)
            for dep in meta.get('dependencies', []):
                install_one(dep)
            pkg_path = path2 if offline else self.cache_mgr.add(path2, name2, ver2)
            pkg_dir = os.path.join(self._env_path(env), 'packages', f"{name2}-{ver2}")
            extract_tar(pkg_path, pkg_dir)
            installed.append({'name': name2, 'version': ver2})
            write_json(installed, self._installed_file(env))

        for r in reqs:
            install_one(r)

    def uninstall(self, env, names):
        if env not in self.list():
            raise click.ClickException(f"Env '{env}' does not exist")
        installed = self.list_installed(env)
        remaining = [p for p in installed if p['name'] not in names]
        for p in installed:
            if p['name'] in names:
                pkg_dir = os.path.join(self._env_path(env), 'packages',
                                       f"{p['name']}-{p['version']}")
                remove_path(pkg_dir)
        write_json(remaining, self._installed_file(env))

    def lock(self, env, lockfile):
        data = {'env': env, 'packages': self.list_installed(env)}
        write_json(data, lockfile)

    def install_lockfile(self, lockfile, env):
        if env in self.list():
            raise click.ClickException(f"Env '{env}' already exists")
        data = read_json(lockfile)
        pkgs = data['packages']
        self.create(env)
        for p in pkgs:
            name, ver = p['name'], p['version']
            path = self.cache_mgr.get(name, ver)
            if not path:
                info = self._find_packages(name, f"=={ver}")
                if not info:
                    raise click.ClickException(f"Package '{name}-{ver}' not found")
                path = self.cache_mgr.add(info['path'], name, ver)
            dst = os.path.join(self._env_path(env), 'packages', f"{name}-{ver}")
            extract_tar(path, dst)
        write_json(pkgs, self._installed_file(env))
