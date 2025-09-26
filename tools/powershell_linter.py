#!/usr/bin/env python3
"""
PowerShell Linting Script
Checks PowerShell scripts for common issues and best practices.
"""

import os
import sys
import argparse
import re
from pathlib import Path


def check_args_variable_usage(content, file_path):
    """Check for usage of $args variable which conflicts with PowerShell's automatic variable."""
    issues = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Look for $args variable assignments or usage
        if re.search(r'\$args\s*[=+\-]', line):
            issues.append(f"{file_path}:{i}: Variable '$args' conflicts with PowerShell's automatic variable. Use a different name like '$arguments' or '$parameters'.")
        elif re.search(r'@args', line):
            issues.append(f"{file_path}:{i}: Using '@args' may conflict with PowerShell's automatic variable. Consider using '@arguments' or '@parameters'.")
    
    return issues


def check_common_powershell_issues(content, file_path):
    """Check for common PowerShell scripting issues."""
    issues = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Check for null comparison best practices
        if re.search(r'\w+\s*-\w+\s*\$null', line):
            issues.append(f"{file_path}:{i}: Consider putting $null on the left side of equality comparisons for better null safety.")
        
        # Check for missing error handling
        if re.search(r'&.*\.ps1', line) and not re.search(r'try\s*\{', line):
            issues.append(f"{file_path}:{i}: Consider adding error handling (try-catch) when calling external scripts.")
        
        # Check for hardcoded paths
        if re.search(r'[A-Z]:\\', line):
            issues.append(f"{file_path}:{i}: Consider using relative paths or environment variables instead of hardcoded absolute paths.")
    
    return issues


def lint_powershell_file(file_path, fix=False):
    """Lint a single PowerShell file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False
    
    issues = []
    
    # Check for $args variable usage
    issues.extend(check_args_variable_usage(content, file_path))
    
    # Check for other common issues
    issues.extend(check_common_powershell_issues(content, file_path))
    
    if issues:
        print(f"Issues found in {file_path}:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print(f"OK: {file_path}")
        return True


def lint_directory(directory, fix=False):
    """Lint all PowerShell files in a directory."""
    issues_found = False
    directory_path = Path(directory)
    
    if not directory_path.exists():
        print(f"Directory {directory} does not exist")
        return True
    
    # Get current working directory to ensure we only scan project files
    cwd = Path.cwd()
    try:
        abs_directory = directory_path.resolve()
        if not str(abs_directory).startswith(str(cwd)):
            print(f"Directory {directory} is outside the project directory. Skipping.")
            return True
    except (OSError, ValueError):
        print(f"Invalid directory path: {directory}")
        return True
    
    ps_files = list(directory_path.rglob("*.ps1"))
    
    # Filter out files that should be ignored
    ignore_patterns = {
        '.venv', 'build', 'build-executables', 'dist', '__pycache__', '.git'
    }
    
    filtered_files = []
    for file_path in ps_files:
        # Check if any part of the path matches ignore patterns
        if not any(pattern in str(file_path) for pattern in ignore_patterns):
            filtered_files.append(file_path)
    
    if not filtered_files:
        print(f"No PowerShell files found in {directory}")
        return True
    
    print(f"Linting {len(filtered_files)} PowerShell files...")
    
    for file_path in filtered_files:
        if not lint_powershell_file(str(file_path), fix):
            issues_found = True
    
    return not issues_found


def main():
    parser = argparse.ArgumentParser(description='PowerShell linting script')
    parser.add_argument('--fix', action='store_true', help='Auto-fix issues where possible')
    parser.add_argument('--directories', nargs='+', default=['scripts/'], 
                       help='Directories to lint (default: scripts/)')
    parser.add_argument('--files', nargs='+', help='Specific files to lint')
    
    args = parser.parse_args()
    
    if args.files:
        all_passed = True
        for file_path in args.files:
            if not lint_powershell_file(file_path, args.fix):
                all_passed = False
    else:
        all_passed = True
        for directory in args.directories:
            if not lint_directory(directory, args.fix):
                all_passed = False
    
    if all_passed:
        print("All PowerShell files are clean!")
        return 0
    else:
        print("PowerShell linting failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
