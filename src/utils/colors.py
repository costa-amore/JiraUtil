"""
Centralized color utility for consistent text coloring across the project.
Replaces emojis with colored text tags for better cross-platform compatibility.
"""

from enum import Enum
from typing import Tuple


class TextTag(Enum):
    """Enum defining all available text tags and their colors."""
    
    # Success/Positive messages (Green)
    SUCCESS = ('[SUCCESS]', '\033[92m', '\033[0m')
    OK = ('[OK]', '\033[92m', '\033[0m')
    
    # Error/Failure messages (Red)
    FAIL = ('[FAIL]', '\033[91m', '\033[0m')
    ERROR = ('[ERROR]', '\033[91m', '\033[0m')
    MISSING = ('[MISSING]', '\033[91m', '\033[0m')
    
    # Warning messages (Orange/Yellow)
    WARN = ('[WARN]', '\033[93m', '\033[0m')
    
    # Information messages (Blue)
    INFO = ('[INFO]', '\033[94m', '\033[0m')
    TEST = ('[TEST]', '\033[94m', '\033[0m')
    FILES = ('[FILES]', '\033[94m', '\033[0m')
    SEARCH = ('[SEARCH]', '\033[94m', '\033[0m')
    CSV = ('[CSV]', '\033[94m', '\033[0m')
    CLI = ('[CLI]', '\033[94m', '\033[0m')
    AUTH = ('[AUTH]', '\033[94m', '\033[0m')
    ARCH = ('[ARCH]', '\033[94m', '\033[0m')
    PERF = ('[PERF]', '\033[94m', '\033[0m')
    FUNC = ('[FUNC]', '\033[94m', '\033[0m')
    RUN = ('[RUN]', '\033[94m', '\033[0m')
    TIP = ('[TIP]', '\033[94m', '\033[0m')
    RETRY = ('[RETRY]', '\033[94m', '\033[0m')
    COLOR = ('[COLOR]', '\033[94m', '\033[0m')
    
    def __init__(self, tag: str, color_code: str, reset_code: str):
        self.tag = tag
        self.color_code = color_code
        self.reset_code = reset_code
    
    def __add__(self, text: str) -> str:
        """Allow concatenation with text: TextTag.SUCCESS + "some text" """
        return f"{self.color_code}{self.tag}{self.reset_code} {text}"
    
    def __str__(self) -> str:
        """Return the colored tag when converted to string."""
        return f"{self.color_code}{self.tag}{self.reset_code}"
    
    @classmethod
    def get_color_map(cls) -> dict:
        """Get a dictionary mapping tags to their color codes."""
        return {tag.value[0]: (tag.value[1], tag.value[2]) for tag in cls}
    
    @classmethod
    def get_all_tags(cls) -> list:
        """Get a list of all available tags."""
        return [tag.value[0] for tag in cls]
    
    @classmethod
    def is_valid_tag(cls, text: str) -> bool:
        """Check if text contains any valid tag."""
        return any(tag.value[0] in text for tag in cls)


def colored_print(text: str) -> None:
    """Print text with consistent color coding based on text tags."""
    color_map = TextTag.get_color_map()
    
    # Find the first matching tag and apply color
    for tag, (color, reset) in color_map.items():
        if tag in text:
            colored_text = text.replace(tag, f"{color}{tag}{reset}")
            print(colored_text)
            return
    
    # No matching tag found, print as-is
    print(text)


def get_colored_text(text: str) -> str:
    """Return colored text without printing it."""
    color_map = TextTag.get_color_map()
    
    # Find the first matching tag and apply color
    for tag, (color, reset) in color_map.items():
        if tag in text:
            return text.replace(tag, f"{color}{tag}{reset}")
    
    # No matching tag found, return as-is
    return text


def validate_text_tags(text: str) -> bool:
    """Validate that all text tags in the string are defined in the enum."""
    import re
    # Find all text tags in the format [TAG]
    tags = re.findall(r'\[([A-Z_]+)\]', text)
    
    valid_tags = TextTag.get_all_tags()
    for tag in tags:
        if f"[{tag}]" not in valid_tags:
            raise ValueError(f"Undefined text tag: [{tag}]. Available tags: {valid_tags}")
    
    return True
