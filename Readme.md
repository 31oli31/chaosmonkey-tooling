# Chaos Monkey Test Suite

This test suite is designed to run various performance and chaos tests against a target environment. It is configurable and extensible, allowing you to define new tests via JSON configuration or by adding custom Python scripts.

## How to Use

### Initial Setup

It is highly recommended to use a Python virtual environment to manage dependencies and avoid conflicts with other projects.

**1. Create a virtual environment:**

```bash
python3 -m venv venv
```

**2. Activate the virtual environment:**

- On macOS and Linux:
```bash
source venv/bin/activate
```
- On Windows:
```bash
.\venv\Scripts\activate
```

**3. Install the required dependencies:**

```bash
pip install -r requirements.txt
```
oder
```bash
venv/bin/pip install -r requirements.txt
```

### Running Tests

Once the setup is complete and the virtual environment is active, execute the entire test suite by running the `run_all_tests.py` script from the project's root directory:

```bash
python3 tools/run_all_tests.py
```

The script will prompt you to enter a name for the test run. This name will be used to create a new folder in the `report/` directory, where all test artifacts, including CSV data, graphs, and a final `report.md`, will be stored.

## How It Works

The test runner executes tests in two phases:

1.  **General Scripts**: It first runs any standalone Python scripts found in the `test_script/` directory. By convention, `general.py` is always executed first. This is useful for simple, one-off tests that don't require complex configuration.
2.  **Configurable Tests**: It then finds all `*.json` files in the `test_script/configs/` directory and runs a configurable HTTP test for each one.

A 1-minute delay is added between each test to allow the environment to stabilize.

### Configuration Files

The JSON configuration files in `test_script/configs/` are the primary way to define complex HTTP tests. Here's an explanation of the available parameters:

```json
{
    "USERNAME": "your_username",
    "PASSWORD": "your_password",
    "URL_TEMPLATE": "https://your-api.com/endpoint/{bhash}",
    "MODE": "batch",
    "SINGLE_REQUEST_DELAY": 1,
    "BATCH_SIZE": 50,
    "TOTAL_REQUESTS": 1000,
    "IDS": ["id_1", "id_2", "id_3"],
    "ID_EXCEL_PATH": "absolute path of excel file"
}
```

-   `USERNAME` & `PASSWORD`: Credentials for basic authentication.
-   `URL_TEMPLATE`: The URL for the request. Use `{bhash}` as a placeholder that will be replaced by an ID during the test.
-   `MODE`: The execution mode. Can be `"single"` or `"batch"`.
-   `SINGLE_REQUEST_DELAY`: The delay in seconds between individual requests or batches.
-   `BATCH_SIZE`: The number of concurrent requests to send when in `"batch"` mode.
-   `TOTAL_REQUESTS`: The total number of requests to execute for the test.
-   `IDS` / `ID_EXCEL_PATH`: The source of the IDs to use in the `URL_TEMPLATE`.
    -   `IDS`: An array of strings to be used as IDs.
    -   `ID_EXCEL_PATH`: The absolute path to an Excel file containing IDs. The file must have a column named `PPID`.

**Note**: You must provide either `IDS` or `ID_EXCEL_PATH` in your configuration, but not both.

### Adding Custom Scripts

You can add your own custom test scripts to the `test_script/` folder. The test runner will automatically execute them and include their generated report sections in the main `report.md`.

For a script to be compatible, it should:
1.  Accept a `--report-folder` command-line argument.
2.  Generate its own artifacts (like a CSV file and a graph) in the provided report folder.
3.  Append its results as a new section to the `report.md` file within that folder.

The `test_script/general.py` file serves as a good example of how to structure a custom test script.