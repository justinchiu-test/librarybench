def stress_test(fn, attempts):
    successes = 0
    for i in range(attempts):
        try:
            fn()
            successes += 1
            print(f"Attempt {i+1}: Success")
        except Exception as e:
            print(f"Attempt {i+1}: Failure: {e}")
    print(f"Total Successes: {successes}/{attempts}")
