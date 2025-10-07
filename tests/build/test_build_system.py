#!/usr/bin/env python3
"""
API-focused tests for the build system.
Tests the build system from the user's perspective, focusing on end-to-end workflows.
"""

import tempfile
import unittest
from pathlib import Path
import shutil
import sys

# Add tools directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))
# Add tests directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from version_manager import VersionManager
from tests.fixtures import (
    create_test_project_structure, 
    create_version_file_with_version,
    run_version_command,
    get_version_from_file,
    get_version_components,
    create_mock_code_change_detector
)


class TestBuildSystemAPI(unittest.TestCase):
    """API-focused tests for the build system."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_project_dir = create_test_project_structure(self.temp_dir)
        
        # Set up version file
        self.version_file = self.test_project_dir / "scripts" / "version.json"
        self.version_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create initial version
        manager = VersionManager(str(self.version_file))
        manager.set_manual_version(1, 0)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_user_can_build_locally_with_version_increment(self):
        """Test that users can build locally and version increments correctly."""
        # Given: Initial version 1.0.0.0
        initial_version = get_version_from_file(self.version_file)
        self.assertEqual(initial_version, "1.0.0.0")
        
        # When: User runs local build (simulates what build script does)
        result = run_version_command(
            ["increment-local-if-changed"], 
            self.version_file, 
            self.test_project_dir
        )
        
        # Then: Should succeed and increment local build
        self.assertEqual(result.returncode, 0)
        new_version = get_version_from_file(self.version_file)
        self.assertEqual(new_version, "1.0.0.1")
    
    def test_user_can_build_for_release_with_version_increment(self):
        """Test that users can build for release and version increments correctly."""
        # Given: Initial version 1.0.0.0
        initial_version = get_version_from_file(self.version_file)
        self.assertEqual(initial_version, "1.0.0.0")
        
        # When: User runs release build
        result = run_version_command(
            ["build", "release"], 
            self.version_file, 
            self.test_project_dir
        )
        
        # Then: Should succeed and increment build, reset local
        self.assertEqual(result.returncode, 0)
        new_version = get_version_from_file(self.version_file)
        self.assertEqual(new_version, "1.0.1.0")
        
        components = get_version_components(self.version_file)
        self.assertEqual(components['build'], 1)
        self.assertEqual(components['local'], 0)
    
    def test_user_can_build_in_ci_without_version_changes(self):
        """Test that CI builds use existing version without changes."""
        # Given: Version that would be committed by release script
        manager = VersionManager(str(self.version_file))
        manager.set_manual_version(1, 0)
        manager.increment_build()  # Simulate what release script does
        self.assertEqual(manager.get_version_string(), "1.0.1.0")
        
        # When: User runs CI build
        result = run_version_command(["build", "ci"], self.version_file)
        
        # Then: Should succeed and not change version
        self.assertEqual(result.returncode, 0)
        self.assertIn("CI build using version: 1.0.1.0", result.stdout)
        
        # Version should remain unchanged
        final_version = get_version_from_file(self.version_file)
        self.assertEqual(final_version, "1.0.1.0")
    
    def test_user_can_manage_versions_through_cli(self):
        """Test that users can manage versions through CLI commands."""
        # Given: Version manager CLI commands
        commands_to_test = [
            (["get"], "1.0.0.0"),
            (["increment-local"], "1.0.0.1"),
            (["increment"], "1.0.1.0"),  # Build increment resets local to 0
            (["set", "3", "0"], "3.0.0.0"),
        ]
        
        # When/Then: Each command should work correctly
        for cmd, expected_version in commands_to_test:
            with self.subTest(command=cmd):
                result = run_version_command(cmd, self.version_file, self.test_project_dir)
                
                self.assertEqual(result.returncode, 0)
                
                # For set command, check the output message
                if cmd[0] == "set":
                    self.assertIn(f"Version set to: {expected_version}", result.stdout)
                else:
                    # For other commands, check the version output
                    self.assertIn(expected_version, result.stdout)
    
    def test_user_gets_correct_executable_version_info(self):
        """Test that users get correct version info for executables."""
        # Given: Version manager with specific version
        manager = VersionManager(str(self.version_file))
        manager.set_manual_version(1, 2)
        manager.increment_build()
        manager.increment_local_build()
        
        # When: Getting file version info
        file_info = manager.get_file_version_info()
        
        # Then: Should have correct format and required fields
        self.assertEqual(file_info["FileVersion"], "1.2.1.1")
        self.assertEqual(file_info["ProductVersion"], "1.2.1.1")
        self.assertEqual(file_info["ProductName"], "JiraUtil")
        self.assertEqual(file_info["OriginalFilename"], "JiraUtil.exe")
        self.assertEqual(file_info["InternalName"], "JiraUtil")
        
        # Should have all required fields
        required_fields = [
            "FileVersion", "ProductVersion", "FileDescription",
            "ProductName", "CompanyName", "LegalCopyright",
            "LegalTrademarks", "OriginalFilename", "InternalName"
        ]
        
        for field in required_fields:
            self.assertIn(field, file_info)
            self.assertIsNotNone(file_info[field])
    
    def test_user_can_handle_code_change_detection(self):
        """Test that users can handle code change detection scenarios."""
        # Given: Mock detectors for different scenarios
        change_detector = create_mock_code_change_detector(has_changes=True)
        no_change_detector = create_mock_code_change_detector(has_changes=False)
        
        # When: Running with code changes
        manager = VersionManager(str(self.version_file), change_detector=change_detector)
        version, was_incremented = manager.increment_local_build_if_changed()
        
        # Then: Should increment when changes detected
        self.assertTrue(was_incremented)
        self.assertEqual(version, "1.0.0.1")
        
        # Reset version file for second test
        manager = VersionManager(str(self.version_file))
        manager.set_manual_version(1, 0)
        
        # When: Running without code changes
        manager = VersionManager(str(self.version_file), change_detector=no_change_detector)
        version, was_incremented = manager.increment_local_build_if_changed()
        
        # Then: Should not increment when no changes detected
        self.assertFalse(was_incremented)
        self.assertEqual(version, "1.0.0.0")
    
    def test_user_can_work_with_version_workflows(self):
        """Test that users can work with complete version workflows."""
        # Given: Version manager
        manager = VersionManager(str(self.version_file))
        
        # When: Performing a complete workflow
        # 1. Set version
        manager.set_manual_version(2, 1)
        self.assertEqual(manager.get_version_string(), "2.1.0.0")
        
        # 2. Local development
        manager.increment_local_build()
        self.assertEqual(manager.get_version_string(), "2.1.0.1")
        
        # 3. Release build
        manager.increment_build()
        self.assertEqual(manager.get_version_string(), "2.1.1.0")
        
        # 4. More local development
        manager.increment_local_build()
        self.assertEqual(manager.get_version_string(), "2.1.1.1")
        
        # 5. New major version
        manager.set_manual_version(3, 0)
        self.assertEqual(manager.get_version_string(), "3.0.0.0")
        
        # Then: All operations should work correctly
        components = get_version_components(self.version_file)
        self.assertEqual(components['major'], 3)
        self.assertEqual(components['minor'], 0)
        self.assertEqual(components['build'], 0)
        self.assertEqual(components['local'], 0)


if __name__ == "__main__":
    unittest.main()
