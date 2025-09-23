#!/usr/bin/env python3
"""
Simple emoji configuration management.
Provides easy configuration via JSON file and environment variables.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any


class EmojiConfig:
    """Simple emoji configuration manager."""
    
    def __init__(self, config_file: str = ".vscode/emoji-config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Default configuration
        default_config = {
            "useEmoji": True,
            "emojiFallbacks": {
                "🔨": "[BUILD]",
                "🧪": "[TEST]",
                "❌": "[FAIL]",
                "✅": "[OK]",
                "ℹ️": "[INFO]",
                "📋": "[VERSION]",
                "📦": "[PACKAGE]",
                "🧹": "[CLEAN]",
                "📊": "[SUMMARY]",
                "📁": "[FILES]",
                "🎉": "[SUCCESS]",
                "💡": "[TIP]"
            }
        }
        
        # Create the config file if it doesn't exist
        self._create_default_config(default_config)
        
        return default_config
    
    def _create_default_config(self, config: Dict[str, Any]) -> None:
        """Create default configuration file if it doesn't exist."""
        try:
            # Ensure the .vscode directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Create the config file with default settings
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"Created emoji configuration file: {self.config_file}")
            print("You can edit this file to enable/disable emojis for your development environment.")
        except Exception as e:
            print(f"Warning: Could not create config file: {e}", file=sys.stderr)
    
    def save_config(self) -> None:
        """Save current configuration to JSON file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}", file=sys.stderr)
    
    def get_use_emoji(self) -> bool:
        """Get whether emojis should be used."""
        # Check environment variable first
        env_value = os.environ.get("USE_EMOJI", "").lower()
        if env_value in ["false", "0", "no"]:
            return False
        elif env_value in ["true", "1", "yes"]:
            return True
        
        # Check config file
        return self.config.get("useEmoji", True)
    
    def set_use_emoji(self, value: bool) -> None:
        """Set whether emojis should be used."""
        self.config["useEmoji"] = value
        self.save_config()
    
    def get_fallbacks(self) -> Dict[str, str]:
        """Get emoji fallback mappings."""
        return self.config.get("emojiFallbacks", {})
    
    def set_fallback(self, emoji: str, fallback: str) -> None:
        """Set a custom emoji fallback."""
        if "emojiFallbacks" not in self.config:
            self.config["emojiFallbacks"] = {}
        self.config["emojiFallbacks"][emoji] = fallback
        self.save_config()
    
    def format_text(self, text: str) -> str:
        """Format text with emoji support or fallbacks."""
        if self.get_use_emoji():
            return text
        
        # Replace emojis with fallbacks
        for emoji, fallback in self.get_fallbacks().items():
            text = text.replace(emoji, fallback)
        
        return text
    
    def get_status(self) -> Dict[str, Any]:
        """Get current configuration status."""
        return {
            "useEmoji": self.get_use_emoji(),
            "configFile": str(self.config_file),
            "configExists": self.config_file.exists(),
            "fallbacks": self.get_fallbacks()
        }


def main():
    """Command line interface for emoji configuration."""
    if len(sys.argv) < 2:
        print("Usage: python emoji_config.py <command> [args...]")
        print("Commands:")
        print("  status                    - Show current configuration")
        print("  enable                    - Enable emojis")
        print("  disable                   - Disable emojis")
        print("  toggle                    - Toggle emoji setting")
        print("  format <text>             - Format text with current settings")
        print("  set-fallback <emoji> <text> - Set custom fallback")
        sys.exit(1)
    
    config = EmojiConfig()
    command = sys.argv[1]
    
    if command == "status":
        status = config.get_status()
        print(f"Emoji display: {'enabled' if status['useEmoji'] else 'disabled'}")
        print(f"Config file: {status['configFile']}")
        print(f"Config exists: {status['configExists']}")
        print(f"Fallbacks: {len(status['fallbacks'])} configured")
    
    elif command == "enable":
        config.set_use_emoji(True)
        print("✅ Emojis enabled")
    
    elif command == "disable":
        config.set_use_emoji(False)
        print("✅ Emojis disabled")
    
    elif command == "toggle":
        current = config.get_use_emoji()
        config.set_use_emoji(not current)
        status = "enabled" if not current else "disabled"
        print(f"✅ Emojis {status}")
    
    elif command == "format":
        if len(sys.argv) < 3:
            print("Error: format command requires text argument")
            sys.exit(1)
        text = " ".join(sys.argv[2:])
        print(config.format_text(text))
    
    elif command == "set-fallback":
        if len(sys.argv) < 4:
            print("Error: set-fallback command requires emoji and text arguments")
            sys.exit(1)
        emoji = sys.argv[2]
        fallback = sys.argv[3]
        config.set_fallback(emoji, fallback)
        print(f"✅ Set fallback: {emoji} -> {fallback}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
