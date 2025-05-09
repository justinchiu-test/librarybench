import click
from .manager import EnvManager
from .repository import RepositoryManager

# Instantiate managers at module level so state (added repos, created envs)
# persists across multiple click invocations in the same process.
_env_mgr = EnvManager()
_repo_mgr = RepositoryManager()

@click.group()
def cli():
    """Top-level entry point."""
    pass

@cli.group()
def env():
    """Manage environments."""
    pass

@env.command("create")
@click.argument("env_name")
def env_create(env_name):
    """Create a new environment."""
    _env_mgr.create_env(env_name)
    click.echo(f"Created env {env_name}")

@cli.command("install")
@click.option("--env", "env_name", required=True, help="Environment name")
@click.argument("packages", nargs=-1, required=True)
def install(env_name, packages):
    """Install one or more packages into an environment."""
    _env_mgr.install_packages(env_name, list(packages))
    # silent success

@cli.command("explain")
@click.option("--env", "env_name", required=True, help="Environment name")
@click.argument("package")
def explain(env_name, package):
    """Explain the lockfile of an installed package."""
    if not _env_mgr.package_exists(env_name, package):
        click.echo(f"Package {package} not installed in env {env_name}")
        return
    lock = _env_mgr.get_lockfile(env_name)
    click.echo(lock)

@cli.group("repos")
def repos():
    """Manage package repositories."""
    pass

@repos.command("add")
@click.argument("path")
def repos_add(path):
    """Add a new repository JSON file."""
    _repo_mgr.add_repo(path)
    click.echo(f"Added repo {path}")

@repos.command("list")
def repos_list():
    """List all repository paths."""
    for path in _repo_mgr.list_repo_paths():
        click.echo(path)
