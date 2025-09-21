# JIRA CSV HELPER

## Purpose

Helper functions to process JIRA CSV exports.
 run JiraCsv.py --help to see ho they work

## Setup (Windows PowerShell)

1. Create a virtual environment:

```powershell
py -3 -m venv .venv
```

2. Activate it (optional; the runner uses the venv directly):

```powershell
. .\.venv\Scripts\Activate.ps1
```

3. Install dependencies (if any):

```powershell
pip install -r requirements.txt
```

**Note**: If you update `requirements.txt` with new dependencies, you'll need to rebuild the virtual environment:

**Quick way (recommended):**
```powershell
./rebuild-venv.ps1
```

This single command will:
- **Create** a new virtual environment if none exists (initial setup)
- **Rebuild** the virtual environment if one already exists (preserving jira_config.env)
- **Install** all dependencies from requirements.txt
- **Set up** jira_config.env from the example file if needed

4. Run the Jira CSV tool using the runner:

```powershell
# Remove newline characters from CSV fields
./run.ps1 .\JiraCsv.py remove-newline .\path\to\jira.csv -o .\jira-no-newlines.csv

# Extract field values to comma-separated text file
./run.ps1 .\JiraCsv.py extract-to-comma-separated-list "Parent key" .\path\to\jira.csv

# Convert dates for European Excel
./run.ps1 .\JiraCsv.py fix-dates-eu .\path\to\jira.csv -o .\jira-eu-dates.csv

# Process issues with specific label (requires Jira connection)
./run.ps1 .\JiraCsv.py JiraTest
```

You can pass through any additional args after the script path.

Alternative: manual venv + python

```powershell
py -3 -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python .\JiraCsv.py remove-newline .\path\to\jira.csv -o .\jira-no-newlines.csv
python .\JiraCsv.py extract-to-comma-separated-list "Parent key" .\path\to\jira.csv
python .\JiraCsv.py fix-dates-eu .\path\to\jira.csv -o .\jira-eu-dates.csv
python .\JiraCsv.py JiraTest
```

## Project Structure

```
Jira_csv_helper/
├── src/                          # Production code
│   ├── __init__.py
│   ├── JiraCsv.py               # Main CLI entry point
│   ├── jira_cleaner.py          # Newline removal functionality
│   ├── jira_dates_eu.py         # European date formatting
│   ├── jira_field_extractor.py # Field value extraction
│   └── jira_test.py             # Jira rule-testing functionality
├── tests/                        # Test code
│   ├── __init__.py
│   ├── run_tests.py             # Test runner
│   └── test_jira_field_extractor.py
├── JiraCsv.py                   # Root entry point
├── run_tests.py                 # Convenience test runner
├── run.ps1                      # PowerShell runner script
├── requirements.txt
└── README.md
```

## JiraTest Command

The `JiraTest` command processes issues with a specified label and updates their status based on summary patterns.

**Pattern**: Issues with summaries matching "I was in <status1> - expected to be in <status2>" will have their status updated to <status1>.

**Usage**:
```powershell
# Using environment variables (recommended) - defaults to "rule-testing" label
$env:JIRA_URL="https://yourcompany.atlassian.net"
$env:JIRA_USERNAME="your.email@company.com"
$env:JIRA_PASSWORD="your_api_token"
./run.ps1 .\JiraCsv.py JiraTest

# Or provide credentials directly
./run.ps1 .\JiraCsv.py JiraTest --jira-url "https://yourcompany.atlassian.net" --username "your.email@company.com" --password "your_api_token"

# Process issues with a different label
./run.ps1 .\JiraCsv.py JiraTest my-custom-label
```

**Configuration**:
- Run `./rebuild-venv.ps1` to set up the environment (automatically copies `jira_config_example.env` to `.venv\jira_config.env`)
- Edit `.venv\jira_config.env` with your Jira credentials
- Use Jira API tokens instead of passwords for better security

## Running Tests

To run the test suite:

```powershell
# Install test dependencies
pip install pytest

# Run all tests
python run_tests.py

# Or run tests directly with pytest
python -m pytest tests/test_jira_field_extractor.py -v
```

