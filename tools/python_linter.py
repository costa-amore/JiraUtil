#!/usr/bin/env python3
"""
Python Linting Script
Runs flake8, black, and isort on Python files to ensure code quality and consistency.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a command and return success status."""
    print(f"[LINT] {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] {description} completed successfully!")
            return True
        else:
            print(f"[ERROR] {description} failed!")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"[ERROR] {description} failed with exception: {e}")
        return False


def run_black_check(files, fix=False):
    """Run black code formatter."""
    if fix:
        command = f"black --check --diff {' '.join(files)}"
        description = "Running black formatter check"
    else:
        command = f"black --check --diff {' '.join(files)}"
        description = "Running black formatter check"
    
    return run_command(command, description)


def run_black_fix(files):
    """Run black code formatter with auto-fix."""
    command = f"black {' '.join(files)}"
    description = "Running black formatter with auto-fix"
    return run_command(command, description)


def run_isort_check(files, fix=False):
    """Run isort import sorter."""
    if fix:
        command = f"isort --check-only --diff {' '.join(files)}"
        description = "Running isort import sorter check"
    else:
        command = f"isort --check-only --diff {' '.join(files)}"
        description = "Running isort import sorter check"
    
    return run_command(command, description)


def run_isort_fix(files):
    """Run isort import sorter with auto-fix."""
    command = f"isort {' '.join(files)}"
    description = "Running isort import sorter with auto-fix"
    return run_command(command, description)


def run_flake8(files):
    """Run flake8 linter."""
    command = f"flake8 {' '.join(files)}"
    description = "Running flake8 linter"
    return run_command(command, description)


def get_python_files(directories):
    """Get all Python files in the specified directories."""
    python_files = []
    
    for directory in directories:
        if not os.path.exists(directory):
            print(f"[WARNING] Directory {directory} does not exist, skipping...")
            continue
            
        # Find all .py files recursively
        for root, dirs, files in os.walk(directory):
            # Skip __pycache__ directories
            dirs[:] = [d for d in dirs if d != '__pycache__']
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
    
    return python_files


def main():
    parser = argparse.ArgumentParser(description='Python linting script')
    parser.add_argument('--fix', action='store_true', help='Auto-fix issues where possible')
    parser.add_argument('--directories', nargs='+', default=['src/', 'tests/', 'tools/'], 
                       help='Directories to lint (default: src/ tests/ tools/)')
    parser.add_argument('--files', nargs='+', help='Specific files to lint')
    
    args = parser.parse_args()
    
    # Get files to lint
    if args.files:
        files = args.files
    else:
        files = get_python_files(args.directories)
    
    if not files:
        print("[WARNING] No Python files found to lint!")
        return 0
    
    print(f"[LINT] Found {len(files)} Python files to lint")
    
    all_passed = True
    
    # Run flake8 (no auto-fix available)
    if not run_flake8(files):
        all_passed = False
    
    # Run black
    if args.fix:
        if not run_black_fix(files):
            all_passed = False
    else:
        if not run_black_check(files, fix=False):
            all_passed = False
    
    # Run isort
    if args.fix:
        if not run_isort_fix(files):
            all_passed = False
    else:
        if not run_isort_check(files, fix=False):
            all_passed = False
    
    if all_passed:
        print("[OK] All Python linting completed successfully!")
        return 0
    else:
        print("[ERROR] Python linting failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
