import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Test retry settings against an endpoint")
    parser.add_argument("--endpoint", required=True, help="Endpoint URL to test")
    parser.add_argument("--retries", type=int, default=3, help="Number of retries")
    parser.add_argument("--backoff", choices=["constant", "exponential"], default="constant")
    args = parser.parse_args()
    print(f"Endpoint: {args.endpoint}")
    print(f"Retries: {args.retries}")
    print(f"Backoff: {args.backoff}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
