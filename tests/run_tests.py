#!/usr/bin/env python3
"""
Comprehensive test runner for JiraUtil project.

This script runs all tests in the tests directory and provides
a comprehensive test report with functional overview.
"""

import subprocess
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Fix Unicode encoding issues on Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

from utils.colors import colored_print, TextTag



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
	colored_print("[TEST] JiraUtil Comprehensive Test Suite")
	print("=" * 60)
	
	test_files = find_test_files()
	
	if not test_files:
		colored_print("[ERROR] No test files found!")
		return False
	
	colored_print(f"[FILES] Found {len(test_files)} test file(s):")
	for i, test_file in enumerate(test_files, 1):
		print(f"  {i:2d}. {Path(test_file).name}")
	
	colored_print("\n[SEARCH] Test Categories:")
	colored_print("  [CSV] CSV Export Commands    - Field extraction, newline removal, date conversion")
	colored_print("  [TEST] Test Fixture Commands  - Pattern parsing, reset/assert operations")
	colored_print("  [CLI]  CLI Commands          - Command parsing, help, status, version")
	colored_print("  [AUTH] Authentication         - Credential management, config validation")
	colored_print("  [ARCH]  Modular Architecture  - Module imports, backward compatibility")
	colored_print("  [WARN]  Error Handling        - File errors, invalid input, edge cases")
	colored_print("  [PERF] Performance           - Large file processing, batch operations")
	colored_print("  [FUNC] Functional Overview    - End-to-end functionality validation")
	colored_print("  [COLOR] Color System Tests    - Text tag validation, color consistency")
	colored_print("  [VERSION] Version Management  - 4-component versioning, build scripts, executables")
	
	colored_print("\n[USAGE] Run specific tests:")
	colored_print("  python tests/run_tests.py testfixture                    # Run testfixture category")
	colored_print("  python tests/run_tests.py test_testfixture_trigger.py    # Run specific file")
	colored_print("  python tests/run_tests.py test_trigger_operation         # Run tests matching pattern")
	colored_print("  python tests/run_tests.py all                            # Run all tests")
	
	colored_print("\n[RUN] Running tests...")
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
		# Use real-time output with unbuffered stdout
		result = subprocess.run(cmd, check=True, capture_output=False, text=True, bufsize=0)
		print("\n" + "=" * 60)
		# Demonstrate new enum usage patterns
		print(TextTag.SUCCESS + "ALL TESTS PASSED!")
		print(f"\n{TextTag.CSV} Test Summary:")
		print(f"  {TextTag.OK} CSV Export Functionality    - Working correctly")
		print(f"  {TextTag.OK} Test Fixture Management     - Working correctly")
		print(f"  {TextTag.OK} CLI Interface               - Working correctly")
		print(f"  {TextTag.OK} Authentication System       - Working correctly")
		print(f"  {TextTag.OK} Modular Architecture        - Working correctly")
		print(f"  {TextTag.OK} Error Handling              - Working correctly")
		print(f"  {TextTag.OK} Performance                 - Working correctly")
		print(f"  {TextTag.OK} Functional Overview         - Working correctly")
		print(f"  {TextTag.OK} Color System Validation     - Working correctly")
		print(f"  {TextTag.OK} Version Management          - Working correctly")
		print(f"\n{TextTag.PERF} JiraUtil is ready for production use!")
		return True
	except subprocess.CalledProcessError as e:
		print(f"\n\033[91m" + "="*60)
		print("❌ TESTS FAILED! ❌")
		print(f"Exit code: {e.returncode}")
		print("="*60 + "\033[0m")
		print("\nPlease review the test output above for details.")
		print("Common issues:")
		print("  - Virtual environment not set up (run: .\\setup-environment.ps1)")
		print("  - Virtual environment not activated (run: .\\.venv\\Scripts\\Activate.ps1)")
		print("  - Import path issues (check src/ directory structure)")
		print("  - Test data issues (check test file paths)")
		return False


def run_specific_test_category(category):
	"""Run tests for a specific category, file, or pattern."""
	category_mapping = {
		"csv": "test_csv_export_commands.py",
		"testfixture": ["test_testfixture_trigger.py", "test_testfixture_assert.py", "test_testfixture_reset.py"],
		"cli": "test_cli_commands.py",
		"overview": "test_functional_overview.py",
		"color": "test_color_system.py",
		"version": "test_version_manager.py",
		"all": None
	}
	
	if category == "all":
		return run_tests()
	
	# Check if it's a direct file path or pattern
	if category.endswith('.py'):
		# Direct file path provided
		test_file = f"tests/{category}" if not category.startswith('tests/') else category
		if not Path(test_file).exists():
			colored_print(f"[ERROR] Test file not found: {test_file}")
			return False
		return run_test_file(test_file, category)
	
	# Check if it's a test method pattern (e.g., "test_trigger_operation_with_multiple_labels")
	if category.startswith('test_'):
		colored_print(f"[TEST] Running tests matching pattern: {category}")
		src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
		cmd = [sys.executable, "-m", "pytest", "-k", category, "-v", "--tb=short"]
		env = os.environ.copy()
		env['PYTHONPATH'] = src_path
		return run_pytest_command_with_env(cmd, f"tests matching '{category}'", env)
	
	# Check if it's a category mapping
	if category not in category_mapping:
		colored_print(f"[ERROR] Unknown category: {category}")
		print(f"Available categories: {', '.join(category_mapping.keys())}")
		print("Or provide:")
		print("  - A test file name (e.g., 'test_testfixture_trigger.py')")
		print("  - A test method pattern (e.g., 'test_trigger_operation')")
		return False
	
	test_files = category_mapping[category]
	
	# Handle both single file and list of files
	if isinstance(test_files, str):
		test_files = [test_files]
	
	# Check if all test files exist
	missing_files = []
	for test_file in test_files:
		full_path = f"tests/{test_file}" if not test_file.startswith('tests/') else test_file
		if not Path(full_path).exists():
			missing_files.append(full_path)
	
	if missing_files:
		colored_print(f"[ERROR] Test file(s) not found: {', '.join(missing_files)}")
		return False
	
	# Run all test files for this category
	success = True
	for test_file in test_files:
		full_path = f"tests/{test_file}" if not test_file.startswith('tests/') else test_file
		if not run_test_file(full_path, f"{category} ({test_file})"):
			success = False
	
	return success


def run_test_file(test_file, description):
	"""Run a specific test file."""
	colored_print(f"[TEST] Running {description} tests...")
	# Add src to Python path for pytest
	src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
	cmd = [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"]
	env = os.environ.copy()
	env['PYTHONPATH'] = src_path
	return run_pytest_command_with_env(cmd, description, env)


def run_pytest_command(cmd, description):
	"""Run a pytest command and handle the result."""
	try:
		# Use real-time output with unbuffered stdout
		result = subprocess.run(cmd, check=True, capture_output=False, text=True, bufsize=0)
		print(f"SUCCESS: {description.title()} tests passed!")
		return True
	except subprocess.CalledProcessError as e:
		print(f"FAILED: {description.title()} tests failed!")
		return False


def run_pytest_command_with_env(cmd, description, env):
	"""Run a pytest command with custom environment and handle the result."""
	try:
		# Use real-time output with unbuffered stdout
		result = subprocess.run(cmd, check=True, capture_output=False, text=True, bufsize=0, env=env)
		print(f"SUCCESS: {description.title()} tests passed!")
		return True
	except subprocess.CalledProcessError as e:
		print(f"FAILED: {description.title()} tests failed!")
		return False


def check_python_environment():
	"""Check if we're running in the correct Python environment."""
	import sys
	import os
	
	# Check if we're in a virtual environment
	venv_python = os.path.join(os.getcwd(), '.venv', 'Scripts', 'python.exe')
	if os.path.exists(venv_python):
		# We're in a project with a virtual environment
		if not sys.executable.endswith('.venv\\Scripts\\python.exe'):
			print("\033[93m[WARN]  WARNING: You're not using the virtual environment Python!\033[0m")
			print(f"   Current Python: {sys.executable}")
			print(f"   Expected Python: {venv_python}")
			print("")
			print("[TIP] To fix this, use one of these methods:")
			print("   1. Use the run script: .\\run.ps1 tests\\run_tests.py")
			print("   2. Use venv Python directly: .\\.venv\\Scripts\\python.exe tests\\run_tests.py")
			print("   3. Activate venv first: .\\.venv\\Scripts\\Activate.ps1")
			print("")
			print("[RETRY] Attempting to continue with current Python...")
			print("   (This may fail if dependencies are missing)")
			print("")

def main():
	"""Main entry point for the test runner."""
	check_python_environment()
	
	if len(sys.argv) > 1:
		category = sys.argv[1].lower()
		success = run_specific_test_category(category)
	else:
		success = run_tests()
	
	return 0 if success else 1


if __name__ == "__main__":
	sys.exit(main())
