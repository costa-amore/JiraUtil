#!/usr/bin/env python3
"""
Tests for the version management system.
Tests the 4-component version format (M.m.b.l) and all version operations.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
import sys

# Add tools directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from version_manager import VersionManager


class TestVersionManager(unittest.TestCase):
    """Test cases for VersionManager class."""
    
    def setUp(self):
        """Set up test environment with temporary version file."""
        self.temp_dir = tempfile.mkdtemp()
        self.version_file = os.path.join(self.temp_dir, "test_version.json")
        self.manager = VersionManager(self.version_file)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.version_file):
            os.remove(self.version_file)
        os.rmdir(self.temp_dir)
    
    def test_default_version_creation(self):
        """Test that default version file is created with 4 components."""
        # Create a new manager with non-existent file
        temp_file = os.path.join(self.temp_dir, "new_version.json")
        manager = VersionManager(temp_file)
        
        version_string = manager.get_version_string()
        self.assertEqual(version_string, "1.0.0.0")
        
        # Check individual components
        major, minor, build, local = manager.get_version_info()
        self.assertEqual(major, 1)
        self.assertEqual(minor, 0)
        self.assertEqual(build, 0)
        self.assertEqual(local, 0)
        
        # Clean up
        os.remove(temp_file)
    
    def test_version_string_format(self):
        """Test that version string follows M.m.b.l format."""
        version_string = self.manager.get_version_string()
        parts = version_string.split('.')
        self.assertEqual(len(parts), 4)
        self.assertTrue(all(part.isdigit() for part in parts))
    
    def test_manual_version_setting(self):
        """Test setting major.minor version manually resets build and local to 0."""
        # Set version to 2.1
        version = self.manager.set_manual_version(2, 1)
        self.assertEqual(version, "2.1.0.0")
        
        # Verify individual components
        major, minor, build, local = self.manager.get_version_info()
        self.assertEqual(major, 2)
        self.assertEqual(minor, 1)
        self.assertEqual(build, 0)
        self.assertEqual(local, 0)
    
    def test_build_increment(self):
        """Test build number incrementing resets local build to 0."""
        # Set initial version
        self.manager.set_manual_version(1, 0)
        
        # Increment local build first
        self.manager.increment_local_build()
        self.assertEqual(self.manager.get_version_string(), "1.0.0.1")
        
        # Increment build (should reset local to 0)
        version = self.manager.increment_build()
        self.assertEqual(version, "1.0.1.0")
        
        # Increment again
        version = self.manager.increment_build()
        self.assertEqual(version, "1.0.2.0")
        
        # Verify local stays 0
        major, minor, build, local = self.manager.get_version_info()
        self.assertEqual(local, 0)
    
    def test_local_build_increment(self):
        """Test local build number incrementing."""
        # Set initial version
        self.manager.set_manual_version(1, 0)
        
        # Increment local build
        version = self.manager.increment_local_build()
        self.assertEqual(version, "1.0.0.1")
        
        # Increment again
        version = self.manager.increment_local_build()
        self.assertEqual(version, "1.0.0.2")
        
        # Verify build stays 0
        major, minor, build, local = self.manager.get_version_info()
        self.assertEqual(build, 0)
    
    def test_mixed_increments(self):
        """Test mixing build and local increments."""
        # Set initial version
        self.manager.set_manual_version(1, 0)
        
        # Increment local build
        version = self.manager.increment_local_build()
        self.assertEqual(version, "1.0.0.1")
        
        # Increment build (should reset local to 0)
        version = self.manager.increment_build()
        self.assertEqual(version, "1.0.1.0")
        
        # Increment local again
        version = self.manager.increment_local_build()
        self.assertEqual(version, "1.0.1.1")
    
    def test_release_build_resets_local(self):
        """Test that release builds reset local build number to 0."""
        # Set version and increment local builds
        self.manager.set_manual_version(1, 0)
        self.manager.increment_local_build()
        self.manager.increment_local_build()
        self.manager.increment_local_build()
        
        # Should be 1.0.0.3
        version = self.manager.get_version_string()
        self.assertEqual(version, "1.0.0.3")
        
        # Increment build (release) - should reset local to 0
        version = self.manager.increment_build()
        self.assertEqual(version, "1.0.1.0")
        
        # Verify local was reset
        major, minor, build, local = self.manager.get_version_info()
        self.assertEqual(local, 0)
    
    def test_manual_reset_after_increments(self):
        """Test that manual version setting resets both build and local to 0."""
        # Set version and increment both
        self.manager.set_manual_version(1, 0)
        self.manager.increment_build()
        self.manager.increment_local_build()
        self.manager.increment_local_build()
        
        # Should be 1.0.1.2
        version = self.manager.get_version_string()
        self.assertEqual(version, "1.0.1.2")
        
        # Set new manual version
        version = self.manager.set_manual_version(2, 0)
        self.assertEqual(version, "2.0.0.0")
        
        # Verify both are reset
        major, minor, build, local = self.manager.get_version_info()
        self.assertEqual(build, 0)
        self.assertEqual(local, 0)
    
    def test_version_persistence(self):
        """Test that version changes are persisted to file."""
        # Set version and increment
        self.manager.set_manual_version(1, 2)
        self.manager.increment_build()
        self.manager.increment_local_build()
        
        # Create new manager with same file
        new_manager = VersionManager(self.version_file)
        
        # Should have same version
        self.assertEqual(new_manager.get_version_string(), "1.2.1.1")
    
    def test_file_version_info(self):
        """Test that file version info includes all 4 components."""
        self.manager.set_manual_version(1, 2)
        self.manager.increment_build()
        self.manager.increment_local_build()
        
        file_info = self.manager.get_file_version_info()
        
        # Should include full version string
        self.assertEqual(file_info["FileVersion"], "1.2.1.1")
        self.assertEqual(file_info["ProductVersion"], "1.2.1.1")
        
        # Should have other required fields
        self.assertIn("FileDescription", file_info)
        self.assertIn("ProductName", file_info)
        self.assertIn("CompanyName", file_info)


class TestVersionManagerCLI(unittest.TestCase):
    """Test cases for VersionManager command line interface."""
    
    def setUp(self):
        """Set up test environment with temporary version file."""
        self.temp_dir = tempfile.mkdtemp()
        self.version_file = os.path.join(self.temp_dir, "test_version.json")
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.version_file):
            os.remove(self.version_file)
        os.rmdir(self.temp_dir)
    
    def test_get_command(self):
        """Test 'get' command returns 4-component version."""
        import subprocess
        
        # Create version file
        manager = VersionManager(self.version_file)
        manager.set_manual_version(1, 2)
        manager.increment_build()
        manager.increment_local_build()
        
        # Test get command
        result = subprocess.run([
            "python", "tools/version_manager.py", "get",
            "--version-file", self.version_file
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "1.2.1.1")
    
    def test_set_command(self):
        """Test 'set' command resets build and local to 0."""
        import subprocess
        
        # Create version file with some increments
        manager = VersionManager(self.version_file)
        manager.set_manual_version(1, 0)
        manager.increment_build()
        manager.increment_local_build()
        
        # Test set command
        result = subprocess.run([
            "python", "tools/version_manager.py", "set", "2", "1",
            "--version-file", self.version_file
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("Version set to: 2.1.0.0", result.stdout)
        self.assertIn("build and local numbers reset to 0", result.stdout)
    
    def test_increment_local_command(self):
        """Test 'increment-local' command."""
        import subprocess
        
        # Create version file
        manager = VersionManager(self.version_file)
        manager.set_manual_version(1, 0)
        
        # Test increment-local command
        result = subprocess.run([
            "python", "tools/version_manager.py", "increment-local",
            "--version-file", self.version_file
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("Local build incremented to: 1.0.0.1", result.stdout)


if __name__ == "__main__":
    unittest.main()
