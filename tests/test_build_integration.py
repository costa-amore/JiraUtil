#!/usr/bin/env python3
"""
Integration tests for build script versioning.
Tests actual build script behavior with version management.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
import subprocess
import shutil
import sys

# Add tools directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from version_manager import VersionManager


class TestBuildIntegration(unittest.TestCase):
    """Integration tests for build script versioning."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_project_dir = os.path.join(self.temp_dir, "test_project")
        os.makedirs(self.test_project_dir)
        
        # Copy necessary files to test directory
        self.copy_test_files()
        
        # Set up version file
        self.version_file = os.path.join(self.test_project_dir, "scripts", "version.json")
        os.makedirs(os.path.dirname(self.version_file), exist_ok=True)
        
        # Create initial version
        manager = VersionManager(self.version_file)
        manager.set_manual_version(1, 0)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def copy_test_files(self):
        """Copy necessary files for testing."""
        project_root = Path(__file__).parent.parent
        
        # Copy tools directory
        shutil.copytree(os.path.join(project_root, "tools"), os.path.join(self.test_project_dir, "tools"))
        
        # Copy scripts directory
        shutil.copytree(os.path.join(project_root, "scripts"), os.path.join(self.test_project_dir, "scripts"))
        
        # Copy source files
        shutil.copytree(os.path.join(project_root, "src"), os.path.join(self.test_project_dir, "src"))
        
        # Copy test files
        shutil.copytree(os.path.join(project_root, "tests"), os.path.join(self.test_project_dir, "tests"))
        
        # Copy individual files
        files_to_copy = [
            "JiraUtil.py", "ju.py", "run.ps1", "setup-environment.ps1",
            "requirements.txt"
        ]
        
        for file in files_to_copy:
            src = os.path.join(project_root, file)
            if os.path.exists(src):
                shutil.copy2(src, self.test_project_dir)
    
    def test_local_build_version_increment(self):
        """Test that local build script increments local build number."""
        # Get initial version
        manager = VersionManager(self.version_file)
        initial_version = manager.get_version_string()
        self.assertEqual(initial_version, "1.0.0.0")
        
        # Simulate local build by running the version increment command
        # that the build script would run
        result = subprocess.run([
            "python", "tools/version_manager.py", "increment-local-if-changed",
            "--version-file", self.version_file
        ], capture_output=True, text=True, cwd=self.test_project_dir)
        
        self.assertEqual(result.returncode, 0)
        
        # Check that local build was incremented
        manager = VersionManager(self.version_file)
        new_version = manager.get_version_string()
        self.assertEqual(new_version, "1.0.0.1")
    
    def test_release_build_version_increment(self):
        """Test that release build increments build number and resets local build."""
        manager = VersionManager(self.version_file)
        self.assertEqual(manager.get_version_string(), "1.0.0.0")
        
        result = subprocess.run([
            "python", "tools/version_manager.py", "build", "release",
            "--version-file", self.version_file
        ], capture_output=True, text=True, cwd=self.test_project_dir)
        
        self.assertEqual(result.returncode, 0)
        
        manager = VersionManager(self.version_file)
        new_version = manager.get_version_string()
        self.assertEqual(new_version, "1.0.1.0")
        
        major, minor, build, local = new_version.split('.')
        self.assertEqual(major, "1")
        self.assertEqual(minor, "0")
        self.assertEqual(build, "1")
        self.assertEqual(local, "0")
    
    def test_version_file_structure_after_operations(self):
        """Test that version file maintains correct structure after operations."""
        manager = VersionManager(self.version_file)
        
        # Perform various operations
        manager.set_manual_version(2, 1)
        manager.increment_build()
        manager.increment_local_build()
        manager.increment_local_build()
        
        # Check final version
        final_version = manager.get_version_string()
        self.assertEqual(final_version, "2.1.1.2")
        
        # Check file structure
        with open(self.version_file, 'r') as f:
            version_data = json.load(f)
        
        expected_data = {
            "major": 2,
            "minor": 1,
            "build": 1,
            "local": 2,
            "description": "JiraUtil - Jira Administration Tool"
        }
        
        for key, value in expected_data.items():
            self.assertEqual(version_data[key], value)
    
    def test_version_consistency_across_operations(self):
        """Test that version remains consistent across multiple operations."""
        manager = VersionManager(self.version_file)
        
        # Test sequence: set -> local increment -> build increment -> local increment
        manager.set_manual_version(1, 0)
        self.assertEqual(manager.get_version_string(), "1.0.0.0")
        
        manager.increment_local_build()
        self.assertEqual(manager.get_version_string(), "1.0.0.1")
        
        manager.increment_build()  # This resets local to 0
        self.assertEqual(manager.get_version_string(), "1.0.1.0")
        
        manager.increment_local_build()
        self.assertEqual(manager.get_version_string(), "1.0.1.1")
        
        # Test reset
        manager.set_manual_version(2, 0)
        self.assertEqual(manager.get_version_string(), "2.0.0.0")
    
    def test_version_manager_cli_commands(self):
        """Test that all version manager CLI commands work correctly."""
        commands_to_test = [
            (["get"], "1.0.0.0"),
            (["increment-local"], "1.0.0.1"),
            (["increment"], "1.0.1.0"),  # Build increment resets local to 0
            (["set", "3", "0"], "3.0.0.0"),
        ]
        
        for cmd, expected_version in commands_to_test:
            with self.subTest(command=cmd):
                result = subprocess.run([
                    "python", "tools/version_manager.py"
                ] + cmd + ["--version-file", self.version_file],
                capture_output=True, text=True, cwd=self.test_project_dir)
                
                self.assertEqual(result.returncode, 0)
                
                # For set command, check the output message
                if cmd[0] == "set":
                    self.assertIn(f"Version set to: {expected_version}", result.stdout)
                else:
                    # For other commands, check the version output
                    self.assertIn(expected_version, result.stdout)


class TestExecutableVersionIntegration(unittest.TestCase):
    """Test executable version information integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.version_file = os.path.join(self.temp_dir, "test_version.json")
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.version_file):
            os.remove(self.version_file)
        os.rmdir(self.temp_dir)
    
    def test_version_info_creation_with_4_components(self):
        """Test that version info creation works with 4-component versions."""
        # Set up version with all components
        manager = VersionManager(self.version_file)
        manager.set_manual_version(1, 2)
        manager.increment_build()
        manager.increment_local_build()
        manager.increment_local_build()
        
        # Test version info creation
        file_info = manager.get_file_version_info()
        
        # Should have correct version
        self.assertEqual(file_info["FileVersion"], "1.2.1.2")
        self.assertEqual(file_info["ProductVersion"], "1.2.1.2")
        
        # Should have all required fields
        required_fields = [
            "FileVersion", "ProductVersion", "FileDescription",
            "ProductName", "CompanyName", "LegalCopyright",
            "LegalTrademarks", "OriginalFilename", "InternalName"
        ]
        
        for field in required_fields:
            self.assertIn(field, file_info)
            self.assertIsNotNone(file_info[field])
            # LegalTrademarks can be empty, so skip the empty check for that field
            if field != "LegalTrademarks":
                self.assertNotEqual(file_info[field], "")


if __name__ == "__main__":
    unittest.main()
