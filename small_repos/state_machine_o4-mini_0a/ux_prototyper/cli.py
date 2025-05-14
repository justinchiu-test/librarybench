import argparse
import uuid
from wizard_engine import WizardEngine

SESSIONS = {}

def scaffold_wizard():
    engine = WizardEngine()
    session_id = uuid.uuid4().hex
    SESSIONS[session_id] = engine
    print(session_id)
    return session_id

def dump_state(session_id):
    engine = SESSIONS.get(session_id)
    if not engine:
        print(f"Session {session_id} not found")
        return None
    print(engine.current_state)
    return engine.current_state

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    scaffold_parser = subparsers.add_parser('scaffold')
    scaffold_parser.add_argument('type', choices=['wizard'])
    dump_parser = subparsers.add_parser('dump-state')
    dump_parser.add_argument('session_id')
    args = parser.parse_args()
    if args.command == 'scaffold':
        scaffold_wizard()
    elif args.command == 'dump-state':
        dump_state(args.session_id)

if __name__ == '__main__':
    main()
