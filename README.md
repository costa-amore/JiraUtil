## Python runner setup (Windows PowerShell)

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
./run.ps1 .\JiraCsv.py clean-jira .\path\to\jira.csv -o .\jira-cleaned.csv
./run.ps1 .\JiraCsv.py fix-dates-eu .\path\to\jira.csv -o .\jira-eu-dates.csv
```

You can pass through any additional args after the script path.

Alternative: manual venv + python

```powershell
py -3 -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python .\JiraCsv.py clean-jira .\path\to\jira.csv -o .\jira-cleaned.csv
python .\JiraCsv.py fix-dates-eu .\path\to\jira.csv -o .\jira-eu-dates.csv
```

