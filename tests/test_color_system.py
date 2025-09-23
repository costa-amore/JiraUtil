"""
Unit tests for the color system and text tag validation.

This module tests the TextTag enum, color functions, and validation
to ensure consistent text coloring across the project.
"""

import pytest
import sys
import os
from io import StringIO
from unittest.mock import patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.colors import TextTag, colored_print, get_colored_text, validate_text_tags


class TestTextTagEnum:
    """Test the TextTag enum functionality."""
    
    def test_enum_values(self):
        """Test that enum values are correctly defined."""
        assert TextTag.SUCCESS.tag == '[SUCCESS]'
        assert TextTag.SUCCESS.color_code == '\033[92m'
        assert TextTag.SUCCESS.reset_code == '\033[0m'
        
        assert TextTag.ERROR.tag == '[ERROR]'
        assert TextTag.ERROR.color_code == '\033[91m'
        assert TextTag.ERROR.reset_code == '\033[0m'
    
    def test_get_all_tags(self):
        """Test getting all available tags."""
        tags = TextTag.get_all_tags()
        assert '[SUCCESS]' in tags
        assert '[OK]' in tags
        assert '[FAIL]' in tags
        assert '[ERROR]' in tags
        assert '[WARN]' in tags
        assert '[INFO]' in tags
        assert len(tags) > 10  # Should have many tags
    
    def test_get_color_map(self):
        """Test getting the color mapping dictionary."""
        color_map = TextTag.get_color_map()
        assert '[SUCCESS]' in color_map
        assert '[ERROR]' in color_map
        assert color_map['[SUCCESS]'] == ('\033[92m', '\033[0m')
        assert color_map['[ERROR]'] == ('\033[91m', '\033[0m')
    
    def test_is_valid_tag(self):
        """Test checking if text contains valid tags."""
        assert TextTag.is_valid_tag("This has [SUCCESS] in it")
        assert TextTag.is_valid_tag("This has [ERROR] in it")
        assert not TextTag.is_valid_tag("This has no tags")
        assert not TextTag.is_valid_tag("This has [INVALID] in it")
    
    def test_enum_concatenation(self):
        """Test the __add__ method for concatenation."""
        result = TextTag.SUCCESS + "All tests passed!"
        expected = '\033[92m[SUCCESS]\033[0m All tests passed!'
        assert result == expected
        
        result = TextTag.ERROR + "Something went wrong!"
        expected = '\033[91m[ERROR]\033[0m Something went wrong!'
        assert result == expected
    
    def test_enum_string_conversion(self):
        """Test the __str__ method for string conversion."""
        result = str(TextTag.SUCCESS)
        expected = '\033[92m[SUCCESS]\033[0m'
        assert result == expected
        
        result = str(TextTag.WARN)
        expected = '\033[93m[WARN]\033[0m'
        assert result == expected


class TestColoredPrint:
    """Test the colored_print function."""
    
    def test_colored_print_success(self):
        """Test printing success messages."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            colored_print("[SUCCESS] All tests passed!")
            output = mock_stdout.getvalue()
            assert '\033[92m[SUCCESS]\033[0m All tests passed!' in output
    
    def test_colored_print_error(self):
        """Test printing error messages."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            colored_print("[ERROR] Something went wrong!")
            output = mock_stdout.getvalue()
            assert '\033[91m[ERROR]\033[0m Something went wrong!' in output
    
    def test_colored_print_warning(self):
        """Test printing warning messages."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            colored_print("[WARN] This is a warning!")
            output = mock_stdout.getvalue()
            assert '\033[93m[WARN]\033[0m This is a warning!' in output
    
    def test_colored_print_info(self):
        """Test printing info messages."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            colored_print("[INFO] Here's some information!")
            output = mock_stdout.getvalue()
            assert '\033[94m[INFO]\033[0m Here\'s some information!' in output
    
    def test_colored_print_no_tag(self):
        """Test printing text without tags."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            colored_print("This has no tags")
            output = mock_stdout.getvalue()
            assert "This has no tags" in output
            assert '\033[' not in output  # No color codes
    
    def test_colored_print_multiple_tags(self):
        """Test that only the first tag gets colored."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            colored_print("[SUCCESS] This has [ERROR] multiple tags")
            output = mock_stdout.getvalue()
            # Should only color the first tag
            assert '\033[92m[SUCCESS]\033[0m' in output
            assert '[ERROR]' in output  # Second tag should be plain


class TestGetColoredText:
    """Test the get_colored_text function."""
    
    def test_get_colored_text_success(self):
        """Test getting colored success text."""
        result = get_colored_text("[SUCCESS] All tests passed!")
        expected = '\033[92m[SUCCESS]\033[0m All tests passed!'
        assert result == expected
    
    def test_get_colored_text_error(self):
        """Test getting colored error text."""
        result = get_colored_text("[ERROR] Something went wrong!")
        expected = '\033[91m[ERROR]\033[0m Something went wrong!'
        assert result == expected
    
    def test_get_colored_text_no_tag(self):
        """Test getting text without tags."""
        result = get_colored_text("This has no tags")
        assert result == "This has no tags"
        assert '\033[' not in result  # No color codes


class TestValidateTextTags:
    """Test the validate_text_tags function."""
    
    def test_validate_valid_tags(self):
        """Test validation with valid tags."""
        # Should not raise an exception
        validate_text_tags("[SUCCESS] All tests passed!")
        validate_text_tags("[ERROR] Something went wrong!")
        validate_text_tags("This has [INFO] and [WARN] tags")
    
    def test_validate_invalid_tags(self):
        """Test validation with invalid tags."""
        with pytest.raises(ValueError, match="Undefined text tag: \\[INVALID\\]"):
            validate_text_tags("This has [INVALID] tag")
        
        with pytest.raises(ValueError, match="Undefined text tag: \\[BAD\\]"):
            validate_text_tags("This has [BAD] and [WORSE] tags")
    
    def test_validate_mixed_tags(self):
        """Test validation with mixed valid and invalid tags."""
        with pytest.raises(ValueError, match="Undefined text tag: \\[INVALID\\]"):
            validate_text_tags("[SUCCESS] This has [INVALID] tag")
    
    def test_validate_no_tags(self):
        """Test validation with no tags."""
        # Should not raise an exception
        validate_text_tags("This has no tags at all")
        validate_text_tags("")


class TestColorSystemIntegration:
    """Test the color system integration and edge cases."""
    
    def test_all_defined_tags_have_colors(self):
        """Test that all defined tags have proper color codes."""
        for tag in TextTag:
            # Each tag should have a color code and reset code
            assert tag.color_code.startswith('\033[')
            assert tag.reset_code == '\033[0m'
            assert len(tag.color_code) > 0
    
    def test_color_consistency(self):
        """Test that similar tags have consistent colors."""
        # Success tags should be green
        assert TextTag.SUCCESS.color_code == '\033[92m'
        assert TextTag.OK.color_code == '\033[92m'
        
        # Error tags should be red
        assert TextTag.FAIL.color_code == '\033[91m'
        assert TextTag.ERROR.color_code == '\033[91m'
        assert TextTag.MISSING.color_code == '\033[91m'
        
        # Warning tags should be yellow/orange
        assert TextTag.WARN.color_code == '\033[93m'
        
        # Info tags should be blue
        assert TextTag.INFO.color_code == '\033[94m'
        assert TextTag.TEST.color_code == '\033[94m'
        assert TextTag.CSV.color_code == '\033[94m'
    
    def test_enum_usage_in_f_strings(self):
        """Test using enum values in f-strings."""
        test_count = 42
        result = f"{TextTag.TEST} Running {test_count} tests..."
        expected = f"\033[94m[TEST]\033[0m Running {test_count} tests..."
        assert result == expected
    
    def test_enum_usage_with_variables(self):
        """Test using enum values with variables."""
        status = "working"
        result = f"{TextTag.OK} System is {status}"
        expected = f"\033[92m[OK]\033[0m System is {status}"
        assert result == expected


class TestColorSystemEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_string(self):
        """Test with empty strings."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            colored_print("")
            output = mock_stdout.getvalue()
            assert output == "\n"  # Just newline
    
    def test_whitespace_only(self):
        """Test with whitespace-only strings."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            colored_print("   ")
            output = mock_stdout.getvalue()
            assert "   " in output
            assert '\033[' not in output  # No color codes
    
    def test_tag_at_end(self):
        """Test with tag at the end of string."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            colored_print("Status: [SUCCESS]")
            output = mock_stdout.getvalue()
            assert '\033[92m[SUCCESS]\033[0m' in output
    
    def test_tag_at_beginning(self):
        """Test with tag at the beginning of string."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            colored_print("[ERROR] Error occurred")
            output = mock_stdout.getvalue()
            assert '\033[91m[ERROR]\033[0m Error occurred' in output
    
    def test_case_sensitivity(self):
        """Test that tags are case sensitive."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            colored_print("[success] lowercase tag")
            output = mock_stdout.getvalue()
            assert "[success] lowercase tag" in output
            assert '\033[' not in output  # No color codes because case doesn't match
