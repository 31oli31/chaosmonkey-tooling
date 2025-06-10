#!/usr/bin/env python3
import argparse
import json
import os
import sys

# Add tools directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
tools_dir = os.path.abspath(os.path.join(script_dir, '..', 'tools'))
sys.path.append(tools_dir)

from test_utils import run_configurable_test

def main():
    parser = argparse.ArgumentParser(description="Run a configurable HTTP test.")
    parser.add_argument("--config", required=True, help="Path to the JSON config file for the test.")
    parser.add_argument("--report-folder", required=True, help="Path to the main report folder.")
    args = parser.parse_args()

    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading config file {args.config}: {e}")
        sys.exit(1)

    # Use the config filename (without extension) as the test name
    test_name = os.path.splitext(os.path.basename(args.config))[0]
    
    run_configurable_test(args.report_folder, test_name, config)

if __name__ == '__main__':
    main() 