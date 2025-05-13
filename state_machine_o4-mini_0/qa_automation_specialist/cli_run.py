import argparse
import asyncio
from simulation_helpers import get_scenarios, run_scenario

def cli_run_tests():
    parser = argparse.ArgumentParser(description="Run simulation scenarios")
    parser.add_argument('--list-scenarios', action='store_true', help='List available scenarios')
    parser.add_argument('--scenario', type=str, help='Run specified scenario')
    args = parser.parse_args()
    if args.list_scenarios:
        for name in get_scenarios().keys():
            print(name)
        return
    if args.scenario:
        try:
            result = asyncio.get_event_loop().run_until_complete(run_scenario(args.scenario))
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")
        return
    parser.print_help()

if __name__ == '__main__':
    cli_run_tests()
