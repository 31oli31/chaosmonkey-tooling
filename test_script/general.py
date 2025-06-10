import argparse
import os
import sys
import time
import requests

# Add tools directory to path to import the new test utilities
script_dir = os.path.dirname(os.path.abspath(__file__))
tools_dir = os.path.abspath(os.path.join(script_dir, '..', 'tools'))
sys.path.append(tools_dir)

from test_utils import run_test_logic

# The name of this test
TEST_NAME = "google_request_example"

def perform_request():
    """
    Performs a single GET request to Google and measures performance.
    Returns duration in milliseconds and the status code.
    """
    url = "https://www.google.de"
    try:
        start_time = time.perf_counter()
        # We don't need the content, so we stream it and don't read the body.
        response = requests.get(url, timeout=10, stream=True)
        end_time = time.perf_counter()
        
        duration_ms = (end_time - start_time) * 1000
        return duration_ms, response.status_code
    except requests.exceptions.RequestException as e:
        print(f"ERROR during request: {e}")
        return -1, 999  # Indicate a failed request

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=f"Run the {TEST_NAME} test.")
    parser.add_argument("--report-folder", required=True, help="Path to the main report folder.")
    args = parser.parse_args()

    # The number of requests for this specific test
    num_requests = 50

    # Call the generic test runner with our specific request logic
    run_test_logic(args.report_folder, TEST_NAME, perform_request, num_requests) 