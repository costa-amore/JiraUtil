# CSV Export Commands

[🏠 Home](../README.md)

> **For users**: See [Command Reference](command-reference.md) for quick command syntax and examples.
> **For developers**: This page provides detailed implementation information.

Commands for processing Jira CSV exports.

## remove-newline

Remove newline characters from CSV fields.

### Usage

```powershell
./run.ps1 .\JiraUtil.py CsvExport remove-newline <input.csv> [--output <output.csv>]

# Short-hand: ./run.ps1 .\ju.py ce rn <input.csv> [--output <output.csv>]
```

### Examples

```powershell

# Remove newlines, create output file automatically
./run.ps1 .\JiraUtil.py CsvExport remove-newline .\jira-export.csv

# Short-hand: ./run.ps1 .\ju.py ce rn .\jira-export.csv

# Specify custom output file
./run.ps1 .\JiraUtil.py CsvExport remove-newline .\jira-export.csv -o .\jira-clean.csv

# Short-hand: ./run.ps1 .\ju.py ce rn .\jira-export.csv -o .\jira-clean.csv
```

### Output

Creates a new CSV file with cleaned data (default: `<input-stem>-no-newlines.csv`)

## extract-to-comma-separated-list

Extract field values from CSV and write to comma-separated text file.

### Extract Usage

```powershell
./run.ps1 .\JiraUtil.py CsvExport extract-to-comma-separated-list <field_name> <input.csv>

# Short-hand: ./run.ps1 .\ju.py ce ecl <field_name> <input.csv>
```

### Extract Examples

```powershell

# Extract Parent key values
./run.ps1 .\JiraUtil.py CsvExport extract-to-comma-separated-list "Parent key" .\jira-export.csv

# Short-hand: ./run.ps1 .\ju.py ce ecl "Parent key" .\jira-export.csv

# Extract Assignee values
./run.ps1 .\JiraUtil.py CsvExport extract-to-comma-separated-list "Assignee" .\jira-export.csv

# Short-hand: ./run.ps1 .\ju.py ce ecl "Assignee" .\jira-export.csv

# Extract Status values
./run.ps1 .\JiraUtil.py CsvExport extract-to-comma-separated-list "Status" .\jira-export.csv

# Short-hand: ./run.ps1 .\ju.py ce ecl "Status" .\jira-export.csv
```

### Extract Output

Creates a text file with comma-separated values (default: `<field_name>.txt`)

## fix-dates-eu

Convert Created/Updated dates for European Excel format.

### Fix Dates Usage

```powershell
./run.ps1 .\JiraUtil.py CsvExport fix-dates-eu <input.csv> [--output <output.csv>]

# Short-hand: ./run.ps1 .\ju.py ce fd <input.csv> [--output <output.csv>]
```

### Fix Dates Examples

```powershell

# Fix dates, create output file automatically
./run.ps1 .\JiraUtil.py CsvExport fix-dates-eu .\jira-export.csv

# Short-hand: ./run.ps1 .\ju.py ce fd .\jira-export.csv

# Specify custom output file
./run.ps1 .\JiraUtil.py CsvExport fix-dates-eu .\jira-export.csv -o .\jira-eu-dates.csv

# Short-hand: ./run.ps1 .\ju.py ce fd .\jira-export.csv -o .\jira-eu-dates.csv
```

### Fix Dates Output

Creates a new CSV file with European date format (default: `<input-stem>-eu-dates.csv`)

## Manual Python Usage

You can also run commands directly with Python:

```powershell

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run commands directly
python .\JiraUtil.py CsvExport remove-newline .\jira-export.csv
python .\JiraUtil.py CsvExport extract-to-comma-separated-list "Parent key" .\jira-export.csv
python .\JiraUtil.py CsvExport fix-dates-eu .\jira-export.csv
```

---

[← Setup Guide](setup.md) | [Jira Commands →](jira-commands.md)
