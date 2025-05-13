import argparse
import json
from .queue import TaskQueue

def main(args=None):
    parser = argparse.ArgumentParser(prog='taskcli')
    sub = parser.add_subparsers(dest='cmd')

    sub_list = sub.add_parser('list')
    sub_list.add_argument('--tenant', help='Tenant ID')

    sub_quota = sub.add_parser('quota')
    sub_quota.add_argument('service', help='Service name')
    sub_quota.add_argument('limit', type=int, help='New quota limit')

    sub_pause = sub.add_parser('pause')
    sub_pause.add_argument('tenant', help='Tenant ID')

    sub_resume = sub.add_parser('resume')
    sub_resume.add_argument('tenant', help='Tenant ID')

    parsed = parser.parse_args(args)
    tq = TaskQueue()

    if parsed.cmd == 'list':
        tasks = tq.list_active(parsed.tenant)
        for t in tasks:
            print(f"{t.id} {t.service} ETA:{t.eta}")
    elif parsed.cmd == 'quota':
        tq.adjust_quota(parsed.service, parsed.limit)
        print(f"Quota for {parsed.service} set to {parsed.limit}")
    elif parsed.cmd == 'pause':
        tq.pause_queue(parsed.tenant)
        print(f"Paused queue for {parsed.tenant}")
    elif parsed.cmd == 'resume':
        tq.resume_queue(parsed.tenant)
        print(f"Resumed queue for {parsed.tenant}")
    else:
        parser.print_help()
