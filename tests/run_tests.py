#!/usr/bin/env python3
"""
Comprehensive test runner for JiraUtil project.

This script runs all tests in the tests directory and provides
a comprehensive test report with functional overview.
"""

import subprocess
import sys
from pathlib import Path


def find_test_files():
	"""Find all test files in the tests directory."""
	tests_dir = Path(__file__).parent
	test_files = []
	
	for file_path in tests_dir.glob("test_*.py"):
		if file_path.name != __file__:
			test_files.append(str(file_path))
	
	return sorted(test_files)


def run_tests():
	"""Run all tests and display comprehensive results."""
	print("🧪 JiraUtil Comprehensive Test Suite")
	print("=" * 60)
	
	test_files = find_test_files()
	
	if not test_files:
		print("ERROR: No test files found!")
		return False
	
	print(f"📁 Found {len(test_files)} test file(s):")
	for i, test_file in enumerate(test_files, 1):
		print(f"  {i:2d}. {Path(test_file).name}")
	
	print("\n🔍 Test Categories:")
	print("  📊 CSV Export Commands    - Field extraction, newline removal, date conversion")
	print("  🧪 Test Fixture Commands  - Pattern parsing, reset/assert operations")
	print("  🖥️  CLI Commands          - Command parsing, help, status, version")
	print("  🔐 Authentication         - Credential management, config validation")
	print("  🏗️  Modular Architecture  - Module imports, backward compatibility")
	print("  ⚠️  Error Handling        - File errors, invalid input, edge cases")
	print("  🚀 Performance           - Large file processing, batch operations")
	print("  📋 Functional Overview    - End-to-end functionality validation")
	
	print("\n🏃 Running tests...")
	print("-" * 60)
	
	# Run pytest with comprehensive output
	cmd = [
		sys.executable, "-m", "pytest"
	] + test_files + [
		"-v",                    # Verbose output
		"--tb=short",           # Short traceback format
		"--strict-markers",     # Strict marker handling
		"--disable-warnings",   # Disable warnings for cleaner output
		"--color=yes"           # Colored output
	]
	
	try:
		result = subprocess.run(cmd, check=True, capture_output=False)
		print("\n" + "=" * 60)
		print("🎉 ALL TESTS PASSED! 🎉")
		print("\n📊 Test Summary:")
		print("  ✅ CSV Export Functionality    - Working correctly")
		print("  ✅ Test Fixture Management     - Working correctly") 
		print("  ✅ CLI Interface               - Working correctly")
		print("  ✅ Authentication System       - Working correctly")
		print("  ✅ Modular Architecture        - Working correctly")
		print("  ✅ Error Handling              - Working correctly")
		print("  ✅ Performance                 - Working correctly")
		print("  ✅ Functional Overview         - Working correctly")
		print("\n🚀 JiraUtil is ready for production use!")
		return True
	except subprocess.CalledProcessError as e:
		print(f"\nFAILED: Tests failed with exit code {e.returncode}")
		print("\nPlease review the test output above for details.")
		print("Common issues:")
		print("  - Virtual environment not set up (run: ./setup-environment.ps1)")
		print("  - Virtual environment not activated (run: .\\.venv\\Scripts\\Activate.ps1)")
		print("  - Import path issues (check src/ directory structure)")
		print("  - Test data issues (check test file paths)")
		return False


def run_specific_test_category(category):
	"""Run tests for a specific category."""
	category_mapping = {
		"csv": "test_csv_export_commands.py",
		"testfixture": "test_testfixture_commands.py", 
		"cli": "test_cli_commands.py",
		"overview": "test_functional_overview.py",
		"all": None
	}
	
	if category not in category_mapping:
		print(f"ERROR: Unknown category: {category}")
		print(f"Available categories: {', '.join(category_mapping.keys())}")
		return False
	
	if category == "all":
		return run_tests()
	
	test_file = f"tests/{category_mapping[category]}"
	if not Path(test_file).exists():
		print(f"ERROR: Test file not found: {test_file}")
		return False
	
	print(f"🧪 Running {category} tests...")
	cmd = [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"]
	
	try:
		result = subprocess.run(cmd, check=True, capture_output=False)
		print(f"SUCCESS: {category.title()} tests passed!")
		return True
	except subprocess.CalledProcessError as e:
		print(f"FAILED: {category.title()} tests failed!")
		return False


def main():
	"""Main entry point for the test runner."""
	if len(sys.argv) > 1:
		category = sys.argv[1].lower()
		success = run_specific_test_category(category)
	else:
		success = run_tests()
	
	return 0 if success else 1


if __name__ == "__main__":
	sys.exit(main())
