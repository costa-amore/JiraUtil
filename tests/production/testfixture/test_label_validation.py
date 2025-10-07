import pytest
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from cli.parser import validate_label_format, format_label_validation_error


class TestLabelValidation:

    # Public test methods (sorted alphabetically)
    @pytest.mark.parametrize("scenario,validation_result,expected_error_message", [
        ("space separated labels", "space_separated", "contains required components"),
        ("unknown error type", "unknown_error", "returns None"),
    ])
    def test_format_label_validation_error_scenarios(self, scenario, validation_result, expected_error_message):
        # Given: Validation result based on scenario
        validation_data = self._create_validation_result_for_scenario(validation_result, "label1 label2", ["label1", "label2"])
        
        # When: Error message is formatted
        error_message = format_label_validation_error(validation_data)
        
        # Then: Should match expected behavior
        if expected_error_message == "returns None":
            assert error_message is None
        else:
            self._assert_error_message(error_message, "label1 label2", ["label1", "label2"], expected_error_message)

    @pytest.mark.parametrize("scenario,input_value,expected_valid,expected_error_type,expected_parts", [
        ("empty string", "", True, None, None),
        ("none input", None, True, None, None),
        ("single label", "single-label", True, None, None),
        ("quoted labels", '"label1,label2"', True, None, None),
        ("single word with spaces", "label with spaces", True, None, None),
        ("three parts", "label1 label2 label3", True, None, None),
        ("space separated labels", "label1 label2", False, "space_separated_labels", ["label1", "label2"]),
    ])
    def test_validate_label_format_scenarios(self, scenario, input_value, expected_valid, expected_error_type, expected_parts):
        # Given: Input value for scenario
        # When: Label format is validated
        result = validate_label_format(input_value)
        
        # Then: Should match expected validation result
        if expected_valid:
            self._assert_valid_result(result, input_value)
        else:
            self._assert_invalid_space_separated_result(result, input_value, expected_parts)

    # Private helper methods (sorted alphabetically)
    def _assert_error_message(self, error_message, expected_value, expected_parts, expected_error_type):
        if expected_error_type == "contains required components":
            assert "Invalid label format: '{}'".format(expected_value) in error_message
            assert "Problem: Multiple labels must be quoted and comma-separated" in error_message
            assert "Solution: Use double quotes around comma-separated labels" in error_message
            assert 'Example: -l "{}"'.format(",".join(expected_parts)) in error_message
            assert 'Or use single labels: -l "{}"'.format(expected_parts[0]) in error_message

    def _assert_invalid_space_separated_result(self, result, expected_value, expected_parts):
        assert result["valid"] == False
        assert result["error_type"] == "space_separated_labels"
        assert result["value"] == expected_value
        assert result["parts"] == expected_parts

    def _assert_valid_result(self, result, expected_value):
        assert result["valid"] == True
        assert result["value"] == expected_value

    def _create_validation_result_for_scenario(self, scenario_type, value, parts):
        if scenario_type == "space_separated":
            return {
                "valid": False,
                "error_type": "space_separated_labels",
                "value": value,
                "parts": parts
            }
        elif scenario_type == "unknown_error":
            return {
                "valid": False,
                "error_type": "unknown_error",
                "value": "test"
            }


if __name__ == "__main__":
    pytest.main([__file__])
