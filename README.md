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

4. Run the Jira CSV tool using the runner:

```powershell
# Remove newline characters from CSV fields
./run.ps1 .\JiraCsv.py remove-newline .\path\to\jira.csv -o .\jira-no-newlines.csv

# Extract parent keys to text file
./run.ps1 .\JiraCsv.py extract-parent-key .\path\to\jira.csv

# Convert dates for European Excel
./run.ps1 .\JiraCsv.py fix-dates-eu .\path\to\jira.csv -o .\jira-eu-dates.csv
```

You can pass through any additional args after the script path.

Alternative: manual venv + python

```powershell
py -3 -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python .\JiraCsv.py remove-newline .\path\to\jira.csv -o .\jira-no-newlines.csv
python .\JiraCsv.py extract-parent-key .\path\to\jira.csv
python .\JiraCsv.py fix-dates-eu .\path\to\jira.csv -o .\jira-eu-dates.csv
```

## Project Structure

```
Jira_csv_helper/
├── src/                          # Production code
│   ├── __init__.py
│   ├── JiraCsv.py               # Main CLI entry point
│   ├── jira_cleaner.py          # Newline removal functionality
│   ├── jira_dates_eu.py         # European date formatting
│   └── jira_parent_extractor.py # Parent key extraction
├── tests/                        # Test code
│   ├── __init__.py
│   ├── run_tests.py             # Test runner
│   └── test_jira_parent_extractor.py
├── JiraCsv.py                   # Root entry point
├── run_tests.py                 # Convenience test runner
├── run.ps1                      # PowerShell runner script
├── requirements.txt
└── README.md
```

## Running Tests

To run the test suite:

```powershell
# Install test dependencies
pip install pytest

# Run all tests
python run_tests.py

# Or run tests directly with pytest
python -m pytest tests/test_jira_parent_extractor.py -v
```

