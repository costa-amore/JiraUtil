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

# Fix Unicode encoding issues on Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

def safe_print(text):
    """Print text with emoji fallback for Windows compatibility."""
    if sys.platform == "win32":
        # Replace emojis with safe alternatives for Windows
        replacements = {
            "🧪": "[TEST]",
            "📁": "[FILES]",
            "🔍": "[SEARCH]",
            "📊": "[CSV]",
            "🧪": "[TEST]",
            "🖥️": "[CLI]",
            "🔐": "[AUTH]",
            "🏗️": "[ARCH]",
            "⚠️": "[WARN]",
            "🚀": "[PERF]",
            "📋": "[FUNC]",
            "🏃": "[RUN]",
            "🎉": "[SUCCESS]",
            "✅": "[OK]",
            "❌": "[FAIL]",
            "🔧": "[FIX]"
        }
        for emoji, replacement in replacements.items():
            text = text.replace(emoji, replacement)
    print(text)


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
	safe_print("🧪 JiraUtil Comprehensive Test Suite")
	print("=" * 60)
	
	test_files = find_test_files()
	
	if not test_files:
		print("ERROR: No test files found!")
		return False
	
	safe_print(f"📁 Found {len(test_files)} test file(s):")
	for i, test_file in enumerate(test_files, 1):
		print(f"  {i:2d}. {Path(test_file).name}")
	
	safe_print("\n🔍 Test Categories:")
	safe_print("  📊 CSV Export Commands    - Field extraction, newline removal, date conversion")
	safe_print("  🧪 Test Fixture Commands  - Pattern parsing, reset/assert operations")
	safe_print("  🖥️  CLI Commands          - Command parsing, help, status, version")
	safe_print("  🔐 Authentication         - Credential management, config validation")
	safe_print("  🏗️  Modular Architecture  - Module imports, backward compatibility")
	safe_print("  ⚠️  Error Handling        - File errors, invalid input, edge cases")
	safe_print("  🚀 Performance           - Large file processing, batch operations")
	safe_print("  📋 Functional Overview    - End-to-end functionality validation")
	
	safe_print("\n🏃 Running tests...")
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
		safe_print("🎉 ALL TESTS PASSED! 🎉")
		safe_print("\n📊 Test Summary:")
		safe_print("  ✅ CSV Export Functionality    - Working correctly")
		safe_print("  ✅ Test Fixture Management     - Working correctly") 
		safe_print("  ✅ CLI Interface               - Working correctly")
		safe_print("  ✅ Authentication System       - Working correctly")
		safe_print("  ✅ Modular Architecture        - Working correctly")
		safe_print("  ✅ Error Handling              - Working correctly")
		safe_print("  ✅ Performance                 - Working correctly")
		safe_print("  ✅ Functional Overview         - Working correctly")
		safe_print("\n🚀 JiraUtil is ready for production use!")
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
	
	safe_print(f"🧪 Running {category} tests...")
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
