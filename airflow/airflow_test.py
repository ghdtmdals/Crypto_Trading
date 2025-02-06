import argparse

def airflow_test1():
    print("Test Message 1: Airflow Operator Test 1")
    return True

def airflow_test2():
    print("Test Message 2: Airflow Operator Test 2")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', type = int)
    args = parser.parse_args()

    assert args.test == 1 or args.test == 2, "Input Only Accepts 1 or 2"

    functions = [airflow_test1, airflow_test2]

    functions[args.test - 1]()