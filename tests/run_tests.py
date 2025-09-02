#!/usr/bin/env python3
"""
Simple test runner for the Jira CSV Helper project.
"""

import subprocess
import sys
from pathlib import Path


def main():
	"""Run all tests in the project."""
	# Get the tests directory (where this script is located)
	tests_dir = Path(__file__).parent
	test_files = list(tests_dir.glob("test_*.py"))
	
	if not test_files:
		print("No test files found.")
		return 1
	
	print(f"Found {len(test_files)} test file(s):")
	for test_file in test_files:
		print(f"  - {test_file}")
	
	print("\nRunning tests...")
	
	try:
		# Run pytest with verbose output from the project root
		project_root = tests_dir.parent
		result = subprocess.run([
			sys.executable, "-m", "pytest", 
			"-v", 
			"--tb=short"
		] + [str(f) for f in test_files], 
		cwd=project_root,
		check=True)
		
		print("\n✅ All tests passed!")
		return 0
		
	except subprocess.CalledProcessError as e:
		print(f"\n❌ Tests failed with exit code {e.returncode}")
		return e.returncode
	except FileNotFoundError:
		print("❌ pytest not found. Please install it with: pip install pytest")
		return 1


if __name__ == "__main__":
	sys.exit(main())
