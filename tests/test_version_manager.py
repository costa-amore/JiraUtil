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
from .fixtures import create_temp_version_file, create_version_manager_with_version


class TestVersionManager(unittest.TestCase):
    """Test cases for VersionManager class."""
    
    def setUp(self):
        """Set up test environment with temporary version file."""
        self.version_file, self.temp_dir = create_temp_version_file()
        self.manager = VersionManager(str(self.version_file))
    
    def tearDown(self):
        """Clean up test environment."""
        if self.version_file.exists():
            self.version_file.unlink()
        os.rmdir(self.temp_dir)
    
    def test_default_version_creation(self):
        """Test that default version file is created with 4 components."""
        # Given: A new manager with non-existent file
        temp_file = Path(self.temp_dir) / "new_version.json"
        manager = VersionManager(str(temp_file))
        
        # When: Getting version string and components
        version_string = manager.get_version_string()
        major, minor, build, local = manager.get_version_info()
        
        # Then: Should have default 4-component version
        self.assertEqual(version_string, "1.0.0.0")
        self.assertEqual(major, 1)
        self.assertEqual(minor, 0)
        self.assertEqual(build, 0)
        self.assertEqual(local, 0)
        
        # Clean up
        temp_file.unlink()
    
    def test_version_string_format(self):
        """Test that version string follows M.m.b.l format."""
        # Given: A version manager with default version
        # When: Getting version string
        version_string = self.manager.get_version_string()
        parts = version_string.split('.')
        
        # Then: Should have 4 numeric components
        self.assertEqual(len(parts), 4)
        self.assertTrue(all(part.isdigit() for part in parts))
    
    def test_manual_version_setting(self):
        """Test setting major.minor version manually resets build and local to 0."""
        # Given: A version manager
        # When: Setting manual version to 2.1
        version = self.manager.set_manual_version(2, 1)
        major, minor, build, local = self.manager.get_version_info()
        
        # Then: Should reset build and local to 0
        self.assertEqual(version, "2.1.0.0")
        self.assertEqual(major, 2)
        self.assertEqual(minor, 1)
        self.assertEqual(build, 0)
        self.assertEqual(local, 0)
    
    def test_build_increment(self):
        """Test build number incrementing resets local build to 0."""
        # Given: Version manager with local build incremented
        self.manager.set_manual_version(1, 0)
        self.manager.increment_local_build()
        self.assertEqual(self.manager.get_version_string(), "1.0.0.1")
        
        # When: Incrementing build number
        version = self.manager.increment_build()
        version2 = self.manager.increment_build()
        major, minor, build, local = self.manager.get_version_info()
        
        # Then: Should reset local to 0 and increment build
        self.assertEqual(version, "1.0.1.0")
        self.assertEqual(version2, "1.0.2.0")
        self.assertEqual(local, 0)
    
    def test_local_build_increment(self):
        """Test local build number incrementing."""
        # Given: Version manager with initial version
        self.manager.set_manual_version(1, 0)
        
        # When: Incrementing local build
        version1 = self.manager.increment_local_build()
        version2 = self.manager.increment_local_build()
        major, minor, build, local = self.manager.get_version_info()
        
        # Then: Should increment local and keep build at 0
        self.assertEqual(version1, "1.0.0.1")
        self.assertEqual(version2, "1.0.0.2")
        self.assertEqual(build, 0)
    
    def test_mixed_increments(self):
        """Test mixing build and local increments."""
        # Given: Version manager with initial version
        self.manager.set_manual_version(1, 0)
        
        # When: Mixing local and build increments
        local_version = self.manager.increment_local_build()
        build_version = self.manager.increment_build()
        final_version = self.manager.increment_local_build()
        
        # Then: Should handle increments correctly
        self.assertEqual(local_version, "1.0.0.1")
        self.assertEqual(build_version, "1.0.1.0")
        self.assertEqual(final_version, "1.0.1.1")
    
    def test_release_build_resets_local(self):
        """Test that release builds reset local build number to 0."""
        # Given: Version manager with multiple local increments
        self.manager.set_manual_version(1, 0)
        self.manager.increment_local_build()
        self.manager.increment_local_build()
        self.manager.increment_local_build()
        self.assertEqual(self.manager.get_version_string(), "1.0.0.3")
        
        # When: Incrementing build (release)
        version = self.manager.increment_build()
        major, minor, build, local = self.manager.get_version_info()
        
        # Then: Should reset local to 0
        self.assertEqual(version, "1.0.1.0")
        self.assertEqual(local, 0)
    
    def test_manual_reset_after_increments(self):
        """Test that manual version setting resets both build and local to 0."""
        # Given: Version manager with build and local increments
        self.manager.set_manual_version(1, 0)
        self.manager.increment_build()
        self.manager.increment_local_build()
        self.manager.increment_local_build()
        self.assertEqual(self.manager.get_version_string(), "1.0.1.2")
        
        # When: Setting manual version
        version = self.manager.set_manual_version(2, 0)
        major, minor, build, local = self.manager.get_version_info()
        
        # Then: Should reset both build and local to 0
        self.assertEqual(version, "2.0.0.0")
        self.assertEqual(build, 0)
        self.assertEqual(local, 0)
    
    def test_version_persistence(self):
        """Test that version changes are persisted to file."""
        # Given: Version manager with specific version
        self.manager.set_manual_version(1, 2)
        self.manager.increment_build()
        self.manager.increment_local_build()
        
        # When: Creating new manager with same file
        new_manager = VersionManager(str(self.version_file))
        
        # Then: Should have same persisted version
        self.assertEqual(new_manager.get_version_string(), "1.2.1.1")
    
    def test_file_version_info(self):
        """Test that file version info includes all 4 components."""
        # Given: Version manager with specific version
        self.manager.set_manual_version(1, 2)
        self.manager.increment_build()
        self.manager.increment_local_build()
        
        # When: Getting file version info
        file_info = self.manager.get_file_version_info()
        
        # Then: Should include full version and required fields
        self.assertEqual(file_info["FileVersion"], "1.2.1.1")
        self.assertEqual(file_info["ProductVersion"], "1.2.1.1")
        self.assertIn("FileDescription", file_info)
        self.assertIn("ProductName", file_info)
        self.assertIn("CompanyName", file_info)


class TestVersionManagerCLI(unittest.TestCase):
    """Test cases for VersionManager command line interface."""
    
    def setUp(self):
        """Set up test environment with temporary version file."""
        self.version_file, self.temp_dir = create_temp_version_file()
    
    def tearDown(self):
        """Clean up test environment."""
        if self.version_file.exists():
            self.version_file.unlink()
        os.rmdir(self.temp_dir)
    
    def test_get_command(self):
        """Test 'get' command returns 4-component version."""
        import subprocess
        
        # Given: Version file with specific version
        manager = VersionManager(str(self.version_file))
        manager.set_manual_version(1, 2)
        manager.increment_build()
        manager.increment_local_build()
        
        # When: Running get command
        result = subprocess.run([
            "python", "tools/version_manager.py", "get",
            "--version-file", str(self.version_file)
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        # Then: Should return correct version
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "1.2.1.1")
    
    def test_set_command(self):
        """Test 'set' command resets build and local to 0."""
        import subprocess
        
        # Given: Version file with some increments
        manager = VersionManager(str(self.version_file))
        manager.set_manual_version(1, 0)
        manager.increment_build()
        manager.increment_local_build()
        
        # When: Running set command
        result = subprocess.run([
            "python", "tools/version_manager.py", "set", "2", "1",
            "--version-file", str(self.version_file)
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        # Then: Should reset build and local to 0
        self.assertEqual(result.returncode, 0)
        self.assertIn("Version set to: 2.1.0.0", result.stdout)
        self.assertIn("build and local numbers reset to 0", result.stdout)
    
    def test_increment_local_command(self):
        """Test 'increment-local' command."""
        import subprocess
        
        # Given: Version file with initial version
        manager = VersionManager(str(self.version_file))
        manager.set_manual_version(1, 0)
        
        # When: Running increment-local command
        result = subprocess.run([
            "python", "tools/version_manager.py", "increment-local",
            "--version-file", str(self.version_file)
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        # Then: Should increment local build
        self.assertEqual(result.returncode, 0)
        self.assertIn("Local build incremented to: 1.0.0.1", result.stdout)


if __name__ == "__main__":
    unittest.main()
