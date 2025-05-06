import click
import os
from .manager import EnvManager
from .repository import RepositoryManager
from .cache import CacheManager

@click.group()
@click.option('--root', help="Root directory for environments")
@click.pass_context
def cli(ctx, root):
    """envmgr: simple environment & package manager"""
    # initialize managers
    repo_mgr = RepositoryManager()
    cache_mgr = CacheManager()
    ctx.obj = EnvManager(root=root, repo_manager=repo_mgr, cache_manager=cache_mgr)

@cli.group()
def env():
    """Manage environments."""
    pass

@env.command('create')
@click.argument('name')
@click.pass_obj
def env_create(mgr, name):
    mgr.create_env(name)
    click.echo(f"Created environment '{name}'.")

@env.command('delete')
@click.argument('name')
@click.pass_obj
def env_delete(mgr, name):
    mgr.delete_env(name)
    click.echo(f"Deleted environment '{name}'.")

@env.command('list')
@click.pass_obj
def env_list(mgr):
    es = mgr.list_envs()
    for e in es:
        click.echo(e)

@cli.command('install')
@click.option('--env', 'env_name', required=True, help="Environment name")
@click.argument('packages', nargs=-1, required=True)
@click.pass_obj
def install(mgr, env_name, packages):
    mgr.install_packages(env_name, list(packages))
    click.echo(f"Installed {', '.join(packages)} into '{env_name}'.")

@cli.command('explain')
@click.option('--env', 'env_name', required=True)
@click.argument('package')
@click.pass_obj
def explain(mgr, env_name, package):
    text = mgr.explain_dependency(env_name, package)
    click.echo(text)

@cli.group()
def lockfile():
    """Lockfile commands."""
    pass

@lockfile.command('export')
@click.option('--env', 'env_name', required=True)
@click.option('--output', 'outfile', required=True)
@click.pass_obj
def lock_export(mgr, env_name, outfile):
    mgr.export_lockfile(env_name, outfile)
    click.echo(f"Exported lockfile to {outfile}")

@lockfile.command('install')
@click.option('--env', 'env_name', required=True)
@click.option('--file', 'infile', required=True)
@click.pass_obj
def lock_install(mgr, env_name, infile):
    mgr.install_from_lockfile(env_name, infile)
    click.echo(f"Installed from lockfile into {env_name}")

@cli.command('import-env')
@click.option('--env', 'env_name', required=True)
@click.option('--file', 'infile', required=True)
@click.pass_obj
def import_env(mgr, env_name, infile):
    mgr.import_env(env_name, infile)
    click.echo(f"Imported environment spec into {env_name}")

@cli.group()
def repos():
    """Manage custom repositories."""
    pass

@repos.command('add')
@click.argument('path')
@click.pass_obj
def repos_add(mgr, path):
    mgr.repo.add_repo(path)
    click.echo(f"Added repo {path}")

@repos.command('remove')
@click.argument('path')
@click.pass_obj
def repos_remove(mgr, path):
    mgr.repo.remove_repo(path)
    click.echo(f"Removed repo {path}")

@repos.command('list')
@click.pass_obj
def repos_list(mgr):
    for r in mgr.repo.list_repos():
        click.echo(r)

@cli.command('check')
@click.option('--env', 'env_name', required=True)
@click.argument('package')
@click.pass_obj
def check(mgr, env_name, package):
    exists = mgr.package_exists(env_name, package)
    click.echo(str(exists))

@cli.command('updates')
@click.option('--env', 'env_name', required=True)
@click.pass_obj
def updates(mgr, env_name):
    notes = mgr.get_update_notifications(env_name)
    if not notes:
        click.echo("All packages up-to-date.")
    else:
        for p, v in notes.items():
            click.echo(f"{p}: {v['current']} -> {v['latest']}")
