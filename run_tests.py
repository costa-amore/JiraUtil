#!/usr/bin/env python3
"""
Convenience test runner for the Jira CSV Helper project.
"""

import subprocess
import sys
from pathlib import Path


def main():
	"""Run all tests in the project."""
	# Run the test runner from the tests directory
	tests_dir = Path(__file__).parent / "tests"
	test_runner = tests_dir / "run_tests.py"
	
	if not test_runner.exists():
		print("❌ Test runner not found. Please ensure tests/run_tests.py exists.")
		return 1
	
	try:
		result = subprocess.run([sys.executable, str(test_runner)], check=True)
		return result.returncode
	except subprocess.CalledProcessError as e:
		return e.returncode
	except FileNotFoundError:
		print("❌ Python not found.")
		return 1


if __name__ == "__main__":
	sys.exit(main())