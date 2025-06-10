import os
import sys
import pandas as pd
from datetime import datetime, timezone, timedelta
import requests
import time
import concurrent.futures

def setup_path():
    """Adds the 'tools' directory to sys.path to allow for module imports."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tools_dir = os.path.abspath(os.path.join(script_dir, '..', 'tools'))
    if tools_dir not in sys.path:
        sys.path.append(tools_dir)

setup_path()
from csv_writer import CsvWriter
from generate_graph import create_graph

def execute_single_request(url: str, auth: tuple, verb: str = 'delete', timeout: int = 10):
    """Executes a single HTTP request and returns the result."""
    start_time = time.time()
    status_code = 'ERROR'
    try:
        if verb.lower() == 'get':
            response = requests.get(url, auth=auth, timeout=timeout)
        else: # Default to DELETE
            response = requests.delete(url, auth=auth, timeout=timeout)
        
        status_code = response.status_code
        response.raise_for_status()
    except requests.RequestException:
        pass
    finally:
        duration_ms = (time.time() - start_time) * 1000
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'duration_ms': duration_ms,
            'status_code': status_code
        }

def generate_report_section(test_name, csv_path, start_time, end_time, detailed=False):
    """
    Calculates performance metrics and generates a markdown report section.
    """
    try:
        df = pd.read_csv(csv_path)
        p90 = df["duration_ms"].quantile(0.90)
        p95 = df["duration_ms"].quantile(0.95)
        mean_duration = df["duration_ms"].mean()
        
        metrics_table = f"""| Metric                | Value          |
|-----------------------|----------------|
| Mean Request Duration | {mean_duration:.2f} ms   |
| 90th Percentile       | {p90:.2f} ms       |
| 95th Percentile       | {p95:.2f} ms       |"""
        
    except Exception as e:
        print(f"ERROR: Could not calculate metrics from {csv_path}: {e}")
        metrics_table = "Performance metrics could not be calculated."

    link_start_time = start_time - timedelta(seconds=30)
    link_end_time = end_time + timedelta(seconds=30)
    
    start_time_iso = link_start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    end_time_iso = link_end_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    start_ts_ms = int(link_start_time.timestamp() * 1000)
    end_ts_ms = int(link_end_time.timestamp() * 1000)

    grafana_url = f"https://grafana.dummy.de/......&from={start_ts_ms}&to={end_ts_ms}"
    kibana_url = f"https://kibana.dummy.de/s/test/app/apm/services/test/overview?comparisonEnabled=true&environment=integration&kuery=&latencyAggregationType=avg&offset=1d&rangeFrom={start_time_iso}&rangeTo={end_time_iso}&serviceGroup=&transactionType=request"
    
    graph_filename = os.path.basename(csv_path).replace('.csv', '.png')

    detailed_section = ""
    if detailed:
        detailed_section = """
### CPU Usage
|Server   | Min  | Max  | Mean |
|---------|------|------|------|
|int-1| FILL | FILL | FILL |
|int-2| FILL | FILL | FILL |

### Memory Usage
|Server   | Last     | Mean     |
|---------|----------|----------|
|int-1| FILL | FILL |
|int-2| FILL | FILL |

### Disk I/O
| Metric                                        | Value      |
|-----------------------------------------------|------------|
| `...integration1-vm.sdb` Read Time              | FILL ms    |
| `...integration2-vm.sdb` Read Time              | FILL µs     |
| `...integration1-vm.sdb` Read Bytes             | FILL kB/s   |
| `...integration2-vm.sdb` Read Bytes             | FILL kB/s  |
"""

    return f"""
## Test Results: {test_name}

### Performance Metrics
{metrics_table}

![Performance Graph](./{graph_filename})
{detailed_section}
### Monitoring Links
- [View in Grafana]({grafana_url})
- [View in Kibana]({kibana_url})

---
"""

def run_configurable_test(report_folder, test_name, config):
    """Runs a configurable test based on the provided dictionary."""
    mode = config.get("MODE", "single")
    delay = config.get("SINGLE_REQUEST_DELAY", 1)
    batch_size = config.get("BATCH_SIZE", 30)
    total_requests = config.get("TOTAL_REQUESTS", 100)
    url_template = config["URL_TEMPLATE"]
    auth = (config.get("USERNAME"), config.get("PASSWORD"))

    print(f"--- Running Test: {test_name} ---")
    print(f"Mode: {mode}, Batch Size: {batch_size}, Total Requests: {total_requests}")

    # Load IDs from either the config array or an Excel file
    ids = []
    if "IDS" in config:
        ids = config["IDS"]
        print(f"Loaded {len(ids)} IDs from the config file.")
    elif "ID_EXCEL_PATH" in config:
        try:
            id_df = pd.read_excel(config["ID_EXCEL_PATH"])
            ids = id_df['PPID'].tolist()
            print(f"Loaded {len(ids)} IDs from {config['ID_EXCEL_PATH']}.")
        except Exception as e:
            print(f"Error loading Excel file: {e}")
    
    if not ids:
        print("ERROR: No IDs found in config or Excel file. Aborting test.")
        return

    output_csv = os.path.join(report_folder, f"{test_name}.csv")
    fieldnames = ['timestamp', 'duration_ms', 'status_code']
    start_time = datetime.now(timezone.utc)

    with CsvWriter(output_csv, fieldnames) as writer, requests.Session() as session:
        req_num = 0
        idx = 0
        if mode == 'batch':
            with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:
                while req_num < total_requests:
                    futures = []
                    for _ in range(batch_size):
                        if req_num >= total_requests: break
                        url = url_template.format(bhash=ids[idx])
                        futures.append(executor.submit(execute_single_request, url, auth))
                        idx = (idx + 1) % len(ids)
                        req_num += 1
                    
                    for future in concurrent.futures.as_completed(futures):
                        writer.writerow(future.result())
                    print(f"Progress: {req_num}/{total_requests} requests")
                    time.sleep(delay)
        else: # single mode
            for i in range(total_requests):
                url = url_template.format(bhash=ids[idx])
                result = execute_single_request(url, auth)
                writer.writerow(result)
                print(f"Request {i+1}/{total_requests} done.")
                idx = (idx + 1) % len(ids)
                time.sleep(delay)

    end_time = datetime.now(timezone.utc)
    print("Data generation complete. Generating artifacts...")
    
    create_graph(report_folder, test_name)
    
    report_path = os.path.join(report_folder, "report.md")
    report_section = generate_report_section(test_name, output_csv, start_time, end_time, detailed=True)
    with open(report_path, "a") as f:
        f.write(report_section)
    
    print(f"Test {test_name} complete.")

def run_test_logic(report_folder, test_name, request_logic_func, num_requests=100):
    """Generic test runner for simple, sequential request functions."""
    print(f"--- Starting simple test: {test_name} ---")
    output_csv = os.path.join(report_folder, f"{test_name}.csv")
    
    start_time = datetime.now(timezone.utc)
    with CsvWriter(output_csv, ['request_num', 'duration_ms', 'status_code']) as writer:
        for i in range(num_requests):
            duration, status = request_logic_func()
            writer.writerow({'request_num': i + 1, 'duration_ms': duration, 'status_code': status})
            print(f"Request {i+1}/{num_requests} -> Status: {status}, Duration: {duration:.2f} ms")
    end_time = datetime.now(timezone.utc)

    create_graph(report_folder, test_name)
    report_path = os.path.join(report_folder, "report.md")
    report_section = generate_report_section(test_name, output_csv, start_time, end_time)
    with open(report_path, "a") as f:
        f.write(report_section)

    print(f"Simple test {test_name} complete.") 