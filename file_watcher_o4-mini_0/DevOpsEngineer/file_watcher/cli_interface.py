import argparse
from .core import (
    FileWatcher,
    SymlinkConfig,
    JenkinsPlugin,
    GitHubActionsPlugin,
    GitLabCIPlugin,
)

def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', dest='dry_run')
    symlink_group = parser.add_mutually_exclusive_group()
    symlink_group.add_argument(
        '--follow-symlinks',
        action='store_const',
        const=SymlinkConfig.FOLLOW,
        dest='symlink',
    )
    symlink_group.add_argument(
        '--ignore-symlinks',
        action='store_const',
        const=SymlinkConfig.IGNORE,
        dest='symlink',
    )
    symlink_group.add_argument(
        '--special-symlinks',
        action='store_const',
        const=SymlinkConfig.SPECIAL,
        dest='symlink',
    )
    parser.add_argument('--ignore-hidden', action='store_true', dest='ignore_hidden')
    parser.add_argument(
        '--throttle-rate',
        type=int,
        default=0,
        dest='throttle_rate',
    )
    parser.add_argument('paths', nargs='*')
    ns = parser.parse_args(args)
    fw = FileWatcher(
        dry_run=ns.dry_run,
        symlink=ns.symlink or SymlinkConfig.FOLLOW,
        ignore_hidden=ns.ignore_hidden,
        throttle_rate=ns.throttle_rate,
    )
    # register default plugins
    fw.register_plugin(JenkinsPlugin())
    fw.register_plugin(GitHubActionsPlugin())
    fw.register_plugin(GitLabCIPlugin())
    # register a print handler
    def print_cb(event):
        print(f"Event: {event.type} {event.path}")
    fw.register_handler('*', '.*', print_cb)
    return fw
