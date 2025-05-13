import argparse
import sys
import requests

def main():
    parser = argparse.ArgumentParser(description="Sync CLI")
    parser.add_argument('command', choices=['sync'], help='Command to run')
    parser.add_argument('--api', default='http://localhost:5000', help='API endpoint')
    parser.add_argument('--config', help='Config file path')
    args = parser.parse_args()

    if args.command == 'sync':
        url = f"{args.api}/sync"
        data = {}
        if args.config:
            data['config'] = args.config
        resp = requests.post(url, json=data)
        if resp.status_code == 202:
            job_id = resp.json().get('job_id')
            print(f"Started job {job_id}")
        else:
            print(f"Error: {resp.text}", file=sys.stderr)
            sys.exit(1)

if __name__ == '__main__':
    main()
