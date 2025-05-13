import argparse
import sys

def run_retry_test(attempts, failures):
    history = []
    def test_func(i):
        if i <= failures:
            raise Exception("Simulated failure")
        return "success"
    for i in range(1, attempts + 1):
        try:
            res = test_func(i)
            history.append(("success", i))
            break
        except Exception:
            history.append(("fail", i))
    return history

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--failures", type=int, default=2)
    args = parser.parse_args()
    hist = run_retry_test(args.attempts, args.failures)
    success = any(status == "success" for status, _ in hist)
    for status, attempt in hist:
        print(f"{attempt}: {status}")
    print("PASS" if success else "FAIL")
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
