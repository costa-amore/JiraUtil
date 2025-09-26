#!/usr/bin/env python3
"""
Simple Markdown Linter
Detects and fixes basic markdown issues like trailing spaces and extra blank lines.
"""

import os
import sys
import argparse
import re
from pathlib import Path


def fix_trailing_spaces(content):
    """Remove trailing spaces from lines."""
    lines = content.split('\n')
    fixed_lines = []
    for line in lines:
        # Remove trailing whitespace but preserve empty lines
        fixed_line = line.rstrip()
        fixed_lines.append(fixed_line)
    return '\n'.join(fixed_lines)


def fix_extra_blank_lines(content):
    """Remove multiple consecutive blank lines, keeping only one."""
    # Replace 3 or more consecutive newlines with 2 newlines
    content = re.sub(r'\n{3,}', '\n\n', content)
    return content


def fix_list_spacing(content):
    """Add blank lines before and after lists."""
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Check if current line is a list item (starts with - or number.)
        is_list_item = re.match(r'^\s*[-*+]\s+', line) or re.match(r'^\s*\d+\.\s+', line)
        
        if is_list_item:
            # Check if previous line is not empty and not a list item
            prev_line = lines[i-1] if i > 0 else ""
            prev_is_list = re.match(r'^\s*[-*+]\s+', prev_line) or re.match(r'^\s*\d+\.\s+', prev_line)
            prev_is_empty = prev_line.strip() == ""
            
            if not prev_is_list and not prev_is_empty and prev_line.strip() != "":
                # Add blank line before list
                fixed_lines.append("")
            
            fixed_lines.append(line)
            
            # Check if next line is not a list item and not empty
            next_line = lines[i+1] if i < len(lines) - 1 else ""
            next_is_list = re.match(r'^\s*[-*+]\s+', next_line) or re.match(r'^\s*\d+\.\s+', next_line)
            next_is_empty = next_line.strip() == ""
            
            if not next_is_list and not next_is_empty and next_line.strip() != "":
                # Add blank line after list
                fixed_lines.append("")
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_header_spacing(content):
    """Add blank lines before headers (except first header after section)."""
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Check if current line is a header (starts with #)
        is_header = re.match(r'^#{1,6}\s+', line)
        
        if is_header:
            # Check if previous line is not empty
            prev_line = lines[i-1] if i > 0 else ""
            prev_is_empty = prev_line.strip() == ""
            
            if not prev_is_empty and prev_line.strip() != "":
                # Add blank line before header
                fixed_lines.append("")
            
            fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_code_block_spacing(content):
    """Add blank lines before and after code blocks."""
    lines = content.split('\n')
    fixed_lines = []
    in_code_block = False
    
    for i, line in enumerate(lines):
        # Check if line starts a code block
        if line.strip().startswith('```'):
            if not in_code_block:
                # Starting code block - add blank line before if previous line is not empty
                prev_line = lines[i-1] if i > 0 else ""
                if prev_line.strip() != "":
                    fixed_lines.append("")
                in_code_block = True
            else:
                # Ending code block - add blank line after if next line is not empty
                next_line = lines[i+1] if i < len(lines) - 1 else ""
                if next_line.strip() != "":
                    fixed_lines.append(line)
                    fixed_lines.append("")
                    continue
                in_code_block = False
            
            fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def lint_markdown_file(file_path, fix=False):
    """Lint a single markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False
    
    fixed_content = original_content
    
    # Apply fixes
    fixed_content = fix_trailing_spaces(fixed_content)
    fixed_content = fix_extra_blank_lines(fixed_content)
    fixed_content = fix_list_spacing(fixed_content)
    fixed_content = fix_header_spacing(fixed_content)
    fixed_content = fix_code_block_spacing(fixed_content)
    
    # Check if any changes were made
    if original_content != fixed_content:
        if fix:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                print(f"Fixed: {file_path}")
                return True
            except Exception as e:
                print(f"Error writing {file_path}: {e}")
                return False
        else:
            print(f"Issues found in: {file_path}")
            return False
    else:
        if fix:
            print(f"OK: {file_path}")
        return True


def lint_directory(directory, fix=False):
    """Lint all markdown files in a directory."""
    issues_found = False
    directory_path = Path(directory)
    
    # Only scan if the directory exists and is within the current working directory
    if not directory_path.exists():
        print(f"Directory {directory} does not exist")
        return True
    
    # Get the current working directory to ensure we only scan project files
    cwd = Path.cwd()
    try:
        # Resolve the directory path to get absolute path
        abs_directory = directory_path.resolve()
        # Check if the directory is within the current working directory
        if not str(abs_directory).startswith(str(cwd)):
            print(f"Directory {directory} is outside the project directory. Skipping.")
            return True
    except (OSError, ValueError):
        print(f"Invalid directory path: {directory}")
        return True
    
    md_files = list(directory_path.rglob("*.md"))
    
    # Filter out files that should be ignored (same as CodeChangeDetector)
    ignore_patterns = {
        '.venv',             # Virtual environment
        'build',             # Build output
        'build-executables', # Build output
        'dist',              # Dist output
        '__pycache__',       # Python cache
        '.git',              # Git directory
    }
    
    filtered_files = []
    for md_file in md_files:
        # Check if any part of the path matches ignore patterns
        should_ignore = False
        for part in md_file.parts:
            if part in ignore_patterns:
                should_ignore = True
                break
        
        if not should_ignore:
            filtered_files.append(md_file)
    
    if not filtered_files:
        print(f"No markdown files found in {directory} (after filtering)")
        return True
    
    for md_file in filtered_files:
        if not lint_markdown_file(md_file, fix):
            issues_found = True
    
    return not issues_found


def main():
    parser = argparse.ArgumentParser(description="Simple Markdown Linter")
    parser.add_argument("paths", nargs="+", help="Files or directories to lint")
    parser.add_argument("--fix", action="store_true", help="Fix issues automatically")
    
    args = parser.parse_args()
    
    all_good = True
    
    for path in args.paths:
        if os.path.isfile(path):
            if not lint_markdown_file(path, args.fix):
                all_good = False
        elif os.path.isdir(path):
            if not lint_directory(path, args.fix):
                all_good = False
        else:
            print(f"Path not found: {path}")
            all_good = False
    
    if all_good:
        print("All markdown files are clean!")
        sys.exit(0)
    else:
        print("Markdown linting issues found!")
        sys.exit(1)


if __name__ == "__main__":
    main()
