import argparse
from pipeline.auth import Auth, AuthError
from pipeline.scheduler import Scheduler

def main():
    """
    Simple command-line interface for listing and running tasks.
    """
    parser = argparse.ArgumentParser(description="Pipeline Management Interface")
    parser.add_argument('--username', required=True, help="Username")
    parser.add_argument('--password', required=True, help="Password")
    parser.add_argument('--action', choices=['list', 'run'], required=True,
                        help="Action to perform: list tasks or run pending tasks")
    args = parser.parse_args()

    auth = Auth()
    # In production, users would be configured elsewhere.
    auth.add_user('admin', 'admin', roles=['admin'])

    try:
        token = auth.login(args.username, args.password)
    except AuthError as e:
        print(f"Authentication failed: {e}")
        return

    scheduler = Scheduler(auth)

    if args.action == 'list':
        print("Scheduled Tasks:")
        for name, task in scheduler.tasks.items():
            print(f"  {name}: {task.state.name}")
    elif args.action == 'run':
        try:
            scheduler.run_pending(token)
            print("Scheduler run completed.")
        except Exception as e:
            print(f"Error running scheduler: {e}")
