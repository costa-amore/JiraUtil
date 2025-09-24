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
    
    def test_release_script_accepts_case_variations_of_windows(self):
        """Test that release script accepts case variations of 'windows' platform."""
        valid_platforms = ["windows", "WINDOWS", "Windows", "wInDoWs"]
        
        for platform in valid_platforms:
            with self.subTest(platform=platform):
                result = subprocess.run([
                    "powershell", "-Command", 
                    f".\\scripts\\release.ps1 -Platform {platform}"
                ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
                
                # Should NOT fail with platform validation error
                self.assertNotIn("Unsupported platform", result.stdout,
                    f"Should not reject '{platform}' platform (case-insensitive)")
                
                # Should NOT mention that only Windows is supported (since it's the correct platform)
                self.assertNotIn("[FAIL] JiraUtil only supports Windows builds", result.stdout,
                    f"Should not show Windows-only message for '{platform}' platform")
    
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
                ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
                
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
    
    def test_release_script_accepts_windows_platform(self):
        """Test that release script accepts 'windows' platform (but may fail for other reasons)."""
        result = subprocess.run([
            "powershell", "-Command", 
            ".\\scripts\\release.ps1 -Platform windows"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        # Should NOT fail with platform validation error
        self.assertNotIn("Unsupported platform 'windows'", result.stdout,
            "Should not reject 'windows' platform")
        
        # Should NOT mention that only Windows is supported (since it's the correct platform)
        self.assertNotIn("[FAIL] JiraUtil only supports Windows builds", result.stdout,
            "Should not show Windows-only message for correct platform")
        
        # May fail for other reasons (like uncommitted changes, git issues, etc.)
        # but should not fail due to platform validation


if __name__ == "__main__":
    unittest.main()
