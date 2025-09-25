"""
Tests for the color system and text tag validation.
"""

import pytest
import sys
import os
from io import StringIO
from unittest.mock import patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.colors import TextTag, colored_print, get_colored_text, validate_text_tags


class TestColorSystem:
    """Test the color system functionality."""
    
    def test_text_tag_enum_functionality(self):
        """Test TextTag enum values, methods, and operations."""
        # Test enum values
        assert TextTag.SUCCESS.tag == '[SUCCESS]'
        assert TextTag.SUCCESS.color_code == '\033[92m'
        assert TextTag.SUCCESS.reset_code == '\033[0m'
        assert TextTag.ERROR.color_code == '\033[91m'
        
        # Test getting all tags
        tags = TextTag.get_all_tags()
        expected_tags = ['[SUCCESS]', '[OK]', '[FAIL]', '[ERROR]', '[WARN]', '[INFO]']
        for tag in expected_tags:
            assert tag in tags
        assert len(tags) > 10
        
        # Test color mapping
        color_map = TextTag.get_color_map()
        assert '[SUCCESS]' in color_map
        assert color_map['[SUCCESS]'] == ('\033[92m', '\033[0m')
        
        # Test tag validation
        assert TextTag.is_valid_tag("This has [SUCCESS] in it")
        assert TextTag.is_valid_tag("This has [ERROR] in it")
        assert not TextTag.is_valid_tag("This has no tags")
        assert not TextTag.is_valid_tag("This has [INVALID] in it")
        
        # Test concatenation
        result = TextTag.SUCCESS + "All tests passed!"
        expected = '\033[92m[SUCCESS]\033[0m All tests passed!'
        assert result == expected
        
        # Test string conversion
        assert str(TextTag.SUCCESS) == '\033[92m[SUCCESS]\033[0m'
        assert str(TextTag.WARN) == '\033[93m[WARN]\033[0m'


    def test_colored_print_functionality(self):
        """Test colored_print function with various message types."""
        test_cases = [
            ("[SUCCESS] All tests passed!", '\033[92m[SUCCESS]\033[0m All tests passed!'),
            ("[ERROR] Something went wrong!", '\033[91m[ERROR]\033[0m Something went wrong!'),
            ("[WARN] This is a warning!", '\033[93m[WARN]\033[0m This is a warning!'),
            ("[INFO] Here's some information!", '\033[94m[INFO]\033[0m Here\'s some information!'),
        ]
        
        for input_text, expected_output in test_cases:
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                colored_print(input_text)
                output = mock_stdout.getvalue()
                assert expected_output in output
        
        # Test text without tags
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            colored_print("This has no tags")
            output = mock_stdout.getvalue()
            assert "This has no tags" in output
            assert '\033[' not in output  # No color codes
        
        # Test multiple tags (only first gets colored)
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            colored_print("[SUCCESS] This has [ERROR] multiple tags")
            output = mock_stdout.getvalue()
            assert '\033[92m[SUCCESS]\033[0m' in output
            assert '[ERROR]' in output  # Second tag should be plain


    def test_get_colored_text_functionality(self):
        """Test get_colored_text function with various inputs."""
        test_cases = [
            ("[SUCCESS] All tests passed!", '\033[92m[SUCCESS]\033[0m All tests passed!'),
            ("[ERROR] Something went wrong!", '\033[91m[ERROR]\033[0m Something went wrong!'),
        ]
        
        for input_text, expected_output in test_cases:
            result = get_colored_text(input_text)
            assert result == expected_output
        
        # Test text without tags
        result = get_colored_text("This has no tags")
        assert result == "This has no tags"
        assert '\033[' not in result  # No color codes


    def test_text_tag_validation(self):
        """Test validate_text_tags function with various inputs."""
        # Test valid tags (should not raise exceptions)
        valid_cases = [
            "[SUCCESS] All tests passed!",
            "[ERROR] Something went wrong!",
            "This has [INFO] and [WARN] tags",
            "This has no tags at all",
            ""
        ]
        
        for text in valid_cases:
            validate_text_tags(text)  # Should not raise
        
        # Test invalid tags (should raise ValueError)
        invalid_cases = [
            ("This has [INVALID] tag", "Undefined text tag: \\[INVALID\\]"),
            ("This has [BAD] and [WORSE] tags", "Undefined text tag: \\[BAD\\]"),
            ("[SUCCESS] This has [INVALID] tag", "Undefined text tag: \\[INVALID\\]")
        ]
        
        for text, expected_error in invalid_cases:
            with pytest.raises(ValueError, match=expected_error):
                validate_text_tags(text)


    def test_color_system_integration_and_edge_cases(self):
        """Test color system integration, consistency, and edge cases."""
        # Test all defined tags have proper color codes
        for tag in TextTag:
            assert tag.color_code.startswith('\033[')
            assert tag.reset_code == '\033[0m'
            assert len(tag.color_code) > 0
        
        # Test color consistency
        assert TextTag.SUCCESS.color_code == '\033[92m'
        assert TextTag.OK.color_code == '\033[92m'
        assert TextTag.FAIL.color_code == '\033[91m'
        assert TextTag.ERROR.color_code == '\033[91m'
        assert TextTag.WARN.color_code == '\033[93m'
        assert TextTag.INFO.color_code == '\033[94m'
        
        # Test enum usage in f-strings
        test_count = 42
        result = f"{TextTag.TEST} Running {test_count} tests..."
        expected = f"\033[94m[TEST]\033[0m Running {test_count} tests..."
        assert result == expected
        
        # Test edge cases
        edge_cases = [
            ("", "\n"),  # Empty string
            ("   ", "   "),  # Whitespace only
            ("Status: [SUCCESS]", '\033[92m[SUCCESS]\033[0m'),  # Tag at end
            ("[ERROR] Error occurred", '\033[91m[ERROR]\033[0m Error occurred'),  # Tag at beginning
        ]
        
        for input_text, expected_content in edge_cases:
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                colored_print(input_text)
                output = mock_stdout.getvalue()
                if expected_content == "\n":
                    assert output == expected_content
                else:
                    assert expected_content in output
        
        # Test case sensitivity
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            colored_print("[success] lowercase tag")
            output = mock_stdout.getvalue()
            assert "[success] lowercase tag" in output
            assert '\033[' not in output  # No color codes because case doesn't match
