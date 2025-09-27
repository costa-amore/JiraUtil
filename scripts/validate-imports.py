#!/usr/bin/env python3
"""
Validate that all imports work correctly after refactoring.
This prevents import issues from reaching the test phase.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def validate_imports():
    """Validate all critical imports work."""
    print("🔍 Validating imports...")
    
    try:
        # Test core imports
        from testfixture.workflow import (
            run_TestFixture_Reset,
            run_assert_expectations, 
            run_trigger_operation,
            _toggle_label_on_issue
        )
        print("✅ testfixture.workflow imports OK")
        
        from testfixture.issue_processor import (
            reset_testfixture_issues,
            assert_testfixture_issues,
            _get_issues_for_processing
        )
        print("✅ testfixture.issue_processor imports OK")
        
        from testfixture.reporter import (
            report_reset_results,
            report_assertion_results,
            report_trigger_results
        )
        print("✅ testfixture.reporter imports OK")
        
        # Test that old function names don't exist
        try:
            from testfixture.workflow import process_issues_by_label
            print("❌ OLD FUNCTION STILL EXISTS: process_issues_by_label")
            return False
        except ImportError:
            print("✅ Old function 'process_issues_by_label' properly removed")
            
        try:
            from testfixture.workflow import assert_issues_expectations
            print("❌ OLD FUNCTION STILL EXISTS: assert_issues_expectations")
            return False
        except ImportError:
            print("✅ Old function 'assert_issues_expectations' properly removed")
            
        print("🎉 All imports validated successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

if __name__ == "__main__":
    success = validate_imports()
    sys.exit(0 if success else 1)
