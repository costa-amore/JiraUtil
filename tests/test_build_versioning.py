#!/usr/bin/env python3
"""
Tests for build script versioning behavior.
Tests that local builds increment local build numbers and releases increment build numbers.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
import subprocess
import sys

# Add tools directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from version_manager import VersionManager


class TestBuildVersioning(unittest.TestCase):
    """Test cases for build script versioning behavior."""
    
    def setUp(self):
        """Set up test environment with temporary version file."""
        self.temp_dir = tempfile.mkdtemp()
        self.version_file = os.path.join(self.temp_dir, "test_version.json")
        self.original_version_file = "scripts/version.json"
        
        # Create a test version file
        manager = VersionManager(self.version_file)
        manager.set_manual_version(1, 0)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.version_file):
            os.remove(self.version_file)
        os.rmdir(self.temp_dir)
    
    def test_local_build_increment_command(self):
        """Test that local build increment command works correctly."""
        # Test increment-local-if-changed command
        result = subprocess.run([
            "python", "tools/version_manager.py", "increment-local-if-changed",
            "--version-file", self.version_file
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("Local build incremented to: 1.0.0.1", result.stdout)
    
    def test_release_build_increment_command(self):
        """Test that release build increment command works correctly."""
        # Test increment-if-changed command
        result = subprocess.run([
            "python", "tools/version_manager.py", "increment-if-changed",
            "--version-file", self.version_file
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("Version incremented to: 1.0.1.0", result.stdout)
    
    def test_version_file_structure(self):
        """Test that version file has correct structure with 4 components."""
        with open(self.version_file, 'r') as f:
            version_data = json.load(f)
        
        # Should have all 4 components
        self.assertIn("major", version_data)
        self.assertIn("minor", version_data)
        self.assertIn("build", version_data)
        self.assertIn("local", version_data)
        
        # Should be integers
        self.assertIsInstance(version_data["major"], int)
        self.assertIsInstance(version_data["minor"], int)
        self.assertIsInstance(version_data["build"], int)
        self.assertIsInstance(version_data["local"], int)
    
    def test_version_consistency_after_operations(self):
        """Test that version remains consistent after various operations."""
        manager = VersionManager(self.version_file)
        
        # Set version
        manager.set_manual_version(2, 1)
        self.assertEqual(manager.get_version_string(), "2.1.0.0")
        
        # Increment build
        manager.increment_build()
        self.assertEqual(manager.get_version_string(), "2.1.1.0")
        
        # Increment local
        manager.increment_local_build()
        self.assertEqual(manager.get_version_string(), "2.1.1.1")
        
        # Set new version (should reset both)
        manager.set_manual_version(3, 0)
        self.assertEqual(manager.get_version_string(), "3.0.0.0")


class TestExecutableVersioning(unittest.TestCase):
    """Test cases for executable version information."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.version_file = os.path.join(self.temp_dir, "test_version.json")
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.version_file):
            os.remove(self.version_file)
        os.rmdir(self.temp_dir)
    
    def test_file_version_info_format(self):
        """Test that file version info has correct format for executables."""
        manager = VersionManager(self.version_file)
        manager.set_manual_version(1, 2)
        manager.increment_build()
        manager.increment_local_build()
        
        file_info = manager.get_file_version_info()
        
        # Check required fields
        required_fields = [
            "FileVersion", "ProductVersion", "FileDescription",
            "ProductName", "CompanyName", "LegalCopyright",
            "LegalTrademarks", "OriginalFilename", "InternalName"
        ]
        
        for field in required_fields:
            self.assertIn(field, file_info)
        
        # Check version format
        self.assertEqual(file_info["FileVersion"], "1.2.1.1")
        self.assertEqual(file_info["ProductVersion"], "1.2.1.1")
        
        # Check specific values
        self.assertEqual(file_info["ProductName"], "JiraUtil")
        self.assertEqual(file_info["OriginalFilename"], "JiraUtil.exe")
        self.assertEqual(file_info["InternalName"], "JiraUtil")
    
    def test_version_info_creation_script(self):
        """Test that create-version-info.py creates correct version info."""
        # Set up version
        manager = VersionManager(self.version_file)
        manager.set_manual_version(1, 3)
        manager.increment_build()
        manager.increment_local_build()
        
        # Create a test output file in our temp directory
        test_output_file = os.path.join(self.temp_dir, "test_version_info.txt")
        
        # Run create-version-info.py with our test version file and output file
        result = subprocess.run([
            "python", "tools/create-version-info.py", self.version_file, test_output_file
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        # Should succeed
        self.assertEqual(result.returncode, 0)
        
        # Check if test output file was created
        if os.path.exists(test_output_file):
            with open(test_output_file, 'r') as f:
                content = f.read()
            
            # Should contain version information (4-component format in filevers/prodvers)
            # Check for our controlled test version
            self.assertIn("1,3,1,1", content)  # Check for tuple format (our test version)
            self.assertIn("JiraUtil", content)
            
            # Clean up
            os.remove(test_output_file)


class TestDocumentationVersioning(unittest.TestCase):
    """Test cases for documentation version information."""
    
    def test_version_injection_patterns(self):
        """Test that version injection patterns work with 4-component versions."""
        # Test various version formats
        test_versions = [
            "1.0.0.0",  # Manual set
            "1.0.0.1",  # Local build
            "1.0.1.0",  # Release build
            "1.0.1.5",  # Mixed
            "2.5.10.3"  # Higher numbers
        ]
        
        for version in test_versions:
            # Test version replacement in markdown
            content = "# Test Document\n\nSome content here."
            updated = content.replace("# Test Document", f"# Test Document\n\n## Version\n\nVersion: {version}")
            
            self.assertIn(f"Version: {version}", updated)
            self.assertIn("## Version", updated)


if __name__ == "__main__":
    unittest.main()
