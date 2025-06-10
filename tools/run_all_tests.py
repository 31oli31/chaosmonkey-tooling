import os
import subprocess
import time
import sys
from datetime import datetime

REPORTS_DIR = "report"
TEST_SCRIPTS_DIR = "test_script"
CONFIG_DIR = os.path.join(TEST_SCRIPTS_DIR, "configs")

def find_test_scripts(directory):
    """Finds executable python scripts, ensuring 'general.py' is first."""
    scripts = [f for f in os.listdir(directory) if f.endswith('.py') and not f.startswith('__') and f != 'run_http_test.py']
    if 'general.py' in scripts:
        scripts.remove('general.py')
        scripts.insert(0, 'general.py')
    return scripts

def find_config_files(directory):
    """Finds all JSON config files in a directory."""
    if not os.path.isdir(directory):
        return []
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.json')]

def create_main_report_file(report_dir, test_run_name):
    """Creates the main report file with a header."""
    report_file_path = os.path.join(report_dir, "report.md")
    header_content = f"# Test Suite Report: {test_run_name}\n\n"
    header_content += f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    template_path = os.path.join(os.path.dirname(__file__), 'default.md')

    try:
        header_content += "This report contains the results of all executed tests.\n\n---\n"
        
        try:
            with open(template_path, 'r') as f:
                template_content = f.read()
        except FileNotFoundError:
            print(f"WARNING: Template file not found at {template_path}. Skipping.")
            template_content = ""

        with open(report_file_path, "w") as f:
            f.write(header_content)
            f.write("\n")
            f.write(template_content)
            f.write("\n---\n")

        print(f"Main report file created at {report_file_path}")
        return report_file_path
    except IOError as e:
        print(f"ERROR: Could not create main report file: {e}")
        return None

def run_command(command):
    """Executes a command and streams its output."""
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        if process.returncode != 0:
             print(f"ERROR: Script finished with exit code {process.returncode}.")

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"ERROR: Failed to execute command: {e}")

if __name__ == "__main__":
    test_run_name = input("Enter a name for this test suite run: ")
    if not test_run_name:
        print("Test suite name cannot be empty.")
        sys.exit(1)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_folder_name = f"{test_run_name.lower().replace(' ', '_')}_{timestamp}"
    report_dir = os.path.join(REPORTS_DIR, report_folder_name)
    os.makedirs(report_dir, exist_ok=True)
    print(f"Created report directory: {report_dir}")

    report_file_path = create_main_report_file(report_dir, test_run_name)
    if not report_file_path:
        sys.exit(1)

    # Run general scripts first
    general_scripts = find_test_scripts(TEST_SCRIPTS_DIR)
    for script in general_scripts:
        script_name = os.path.splitext(script)[0]
        print(f"\n--- Running General Test: {script_name} ---")
        test_script_path = os.path.join(TEST_SCRIPTS_DIR, script)
        command = [sys.executable, test_script_path, "--report-folder", report_dir]
        run_command(command)
        print("\nWaiting 1 minute before next test...")
        time.sleep(60)

    # Run configurable tests
    config_files = find_config_files(CONFIG_DIR)
    print(f"Found {len(config_files)} test configurations.")

    for config_path in config_files:
        config_name = os.path.splitext(os.path.basename(config_path))[0]
        print(f"\n--- Running Configurable Test: {config_name} ---")
        
        test_script_path = os.path.join(TEST_SCRIPTS_DIR, "run_http_test.py")
        command = [sys.executable, test_script_path, "--config", config_path, "--report-folder", report_dir]
        run_command(command)

        if config_path != config_files[-1]:
            print("\nWaiting 1 minute before next test...")
            time.sleep(60)

    print(f"\n✅ All tests complete. Final report available at: {report_file_path}") 