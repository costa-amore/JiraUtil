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

4. Run a script using the runner:

```powershell
./run.ps1 .\main.py --name "World"
```

You can pass through any additional args after the script path.

