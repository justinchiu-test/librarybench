import sys
import argparse
from retry_toolkit import retry

def main():
    parser = argparse.ArgumentParser(description="Simulate flaky function with retry")
    parser.add_argument('--failures', type=int, default=1, help="Number of times to fail before success")
    parser.add_argument('--attempts', type=int, default=3, help="Retry attempts")
    args = parser.parse_args()

    state = {'count': 0}

    @retry(attempts=args.attempts)
    def flaky():
        if state['count'] < args.failures:
            state['count'] += 1
            raise ValueError("fail")
        return "ok"

    try:
        result = flaky()
        print(result)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
