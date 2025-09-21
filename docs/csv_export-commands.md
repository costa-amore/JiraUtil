# CSV Commands

Commands for processing Jira CSV exports.

## remove-newline

Remove newline characters from CSV fields.

### Usage

```powershell
./run.ps1 .\JiraUtil.py remove-newline <input.csv> [--output <output.csv>]
```

### Examples

```powershell
# Remove newlines, create output file automatically
./run.ps1 .\JiraUtil.py remove-newline .\jira-export.csv

# Specify custom output file
./run.ps1 .\JiraUtil.py remove-newline .\jira-export.csv -o .\jira-clean.csv
```

### Output

Creates a new CSV file with cleaned data (default: `<input-stem>-no-newlines.csv`)

## extract-to-comma-separated-list

Extract field values from CSV and write to comma-separated text file.

### Usage

```powershell
./run.ps1 .\JiraUtil.py extract-to-comma-separated-list <field_name> <input.csv>
```

### Examples

```powershell
# Extract Parent key values
./run.ps1 .\JiraUtil.py extract-to-comma-separated-list "Parent key" .\jira-export.csv

# Extract Assignee values
./run.ps1 .\JiraUtil.py extract-to-comma-separated-list "Assignee" .\jira-export.csv

# Extract Status values
./run.ps1 .\JiraUtil.py extract-to-comma-separated-list "Status" .\jira-export.csv
```

### Output

Creates a text file with comma-separated values (default: `<field_name>.txt`)

## fix-dates-eu

Convert Created/Updated dates for European Excel format.

### Usage

```powershell
./run.ps1 .\JiraUtil.py fix-dates-eu <input.csv> [--output <output.csv>]
```

### Examples

```powershell
# Fix dates, create output file automatically
./run.ps1 .\JiraUtil.py fix-dates-eu .\jira-export.csv

# Specify custom output file
./run.ps1 .\JiraUtil.py fix-dates-eu .\jira-export.csv -o .\jira-eu-dates.csv
```

### Output

Creates a new CSV file with European date format (default: `<input-stem>-eu-dates.csv`)

## Manual Python Usage

You can also run commands directly with Python:

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run commands directly
python .\JiraUtil.py remove-newline .\jira-export.csv
python .\JiraUtil.py extract-to-comma-separated-list "Parent key" .\jira-export.csv
python .\JiraUtil.py fix-dates-eu .\jira-export.csv
```

---

[← Setup Guide](setup.md) | [Jira Automations Commands →](jira_automations-commands.md)
