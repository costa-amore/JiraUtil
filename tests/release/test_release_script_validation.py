#!/usr/bin/env python3
"""
Tests for release script platform validation.
Tests that the release script gives clear errors for unsupported platforms.
"""

import subprocess
import unittest
from pathlib import Path


class TestReleaseScriptValidation(unittest.TestCase):
    """Test cases for release script platform validation."""
    
    def test_release_script_rejects_invalid_platforms(self):
        """Test that release script rejects invalid platforms with clear error messages."""
        test_cases = [
            ("all", "[FAIL] Unsupported platform 'all'"),
            ("macos", "[FAIL] Unsupported platform 'macos'"),
            ("linux", "[FAIL] Unsupported platform 'linux'"),
            ("invalid", "[FAIL] Unsupported platform 'invalid'"),
        ]
        
        for platform, expected_error in test_cases:
            with self.subTest(platform=platform):
                result = subprocess.run([
                    "powershell", "-Command", 
                    f".\\scripts\\release.ps1 -Platform {platform}"
                ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
                
                # Should fail with exit code 1
                self.assertEqual(result.returncode, 1, 
                    f"Expected exit code 1 for platform '{platform}', got {result.returncode}")
                
                # Should contain the platform-specific error message
                self.assertIn(f"Unsupported platform '{platform}'", result.stdout,
                    f"Expected platform-specific error message not found in output for platform '{platform}'")
                
                # Should mention that only Windows is supported
                self.assertIn("JiraUtil only supports Windows builds", result.stdout,
                    f"Should mention Windows-only support for platform '{platform}'")
                
                # Should show the correct usage
                self.assertIn("Use: .\\scripts\\release.ps1 -Platform windows", result.stdout,
                    f"Should show correct usage for platform '{platform}'")


if __name__ == "__main__":
    unittest.main()
