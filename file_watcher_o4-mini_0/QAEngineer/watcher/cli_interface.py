import argparse
import sys

from .watcher import Watcher
from .plugins.gitlab_ci import GitLabCIPlugin

def main():
    parser = argparse.ArgumentParser(description='File Watcher')
    parser.add_argument('paths', nargs='+')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--no-symlinks', action='store_true')
    parser.add_argument('--debounce', type=float, default=0.5)
    parser.add_argument('--poll', type=float, default=1.0)
    parser.add_argument('--max-retries', type=int, default=3)
    parser.add_argument('--retry-delay', type=float, default=0.1)
    parser.add_argument('--no-hidden-filter', action='store_true')
    parser.add_argument('--gitlab-project')
    parser.add_argument('--gitlab-token')
    args = parser.parse_args()

    watcher = Watcher(
        args.paths,
        dry_run=args.dry_run,
        follow_symlinks=not args.no_symlinks,
        debounce_interval=args.debounce,
        poll_interval=args.poll,
        max_retries=args.max_retries,
        retry_delay=args.retry_delay,
        hidden_filter=not args.no_hidden_filter
    )

    if args.gitlab_project and args.gitlab_token:
        plugin = GitLabCIPlugin(args.gitlab_project, args.gitlab_token)
        watcher.add_plugin(plugin)

    watcher.register_handler('create', lambda p, e: print(f'{e}:{p}'))
    watcher.start()

if __name__ == '__main__':
    main()
