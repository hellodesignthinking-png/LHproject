#!/usr/bin/env python3
"""
ZeroSite v7.0 Rebranding Script
Replaces all instances of "ZeroSite" with "ZeroSite" across the codebase
"""

import os
import re
from pathlib import Path
from typing import List, Tuple


def rebrand_file(file_path: Path) -> Tuple[bool, int]:
    """
    Replace "ZeroSite" with "ZeroSite" in a single file
    
    Returns:
        (modified, replacement_count)
    """
    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count and replace
        original_content = content
        replacement_count = content.count("ZeroSite")
        
        if replacement_count > 0:
            content = content.replace("ZeroSite", "ZeroSite")
            
            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return (True, replacement_count)
        
        return (False, 0)
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return (False, 0)


def rebrand_project(root_dir: str = "/home/user/webapp") -> dict:
    """
    Rebrand entire project
    
    Returns:
        Statistics dictionary
    """
    root = Path(root_dir)
    
    # File patterns to process
    patterns = ['*.md', '*.py', '*.html', '*.css', '*.js', '*.txt', '*.sh']
    
    # Directories to skip
    skip_dirs = {'.git', '__pycache__', 'node_modules', 'venv', '.venv', 'env'}
    
    stats = {
        'files_scanned': 0,
        'files_modified': 0,
        'total_replacements': 0,
        'modified_files': []
    }
    
    print("="*70)
    print("  ZeroSite v7.0 Rebranding Script")
    print("  Replacing 'ZeroSite' → 'ZeroSite'")
    print("="*70)
    print()
    
    # Scan all files
    all_files = []
    for pattern in patterns:
        all_files.extend(root.rglob(pattern))
    
    # Filter out files in skip directories
    filtered_files = []
    for file_path in all_files:
        if not any(skip_dir in file_path.parts for skip_dir in skip_dirs):
            filtered_files.append(file_path)
    
    print(f"Found {len(filtered_files)} files to process")
    print()
    
    # Process each file
    for file_path in filtered_files:
        stats['files_scanned'] += 1
        
        modified, count = rebrand_file(file_path)
        
        if modified:
            stats['files_modified'] += 1
            stats['total_replacements'] += count
            stats['modified_files'].append(str(file_path.relative_to(root)))
            
            print(f"✅ {file_path.relative_to(root)}")
            print(f"   Replaced: {count} occurrence(s)")
    
    return stats


def print_summary(stats: dict):
    """Print summary of rebranding operation"""
    print()
    print("="*70)
    print("  Rebranding Summary")
    print("="*70)
    print()
    print(f"Files scanned:      {stats['files_scanned']}")
    print(f"Files modified:     {stats['files_modified']}")
    print(f"Total replacements: {stats['total_replacements']}")
    print()
    
    if stats['modified_files']:
        print("Modified files:")
        for file_path in stats['modified_files'][:20]:  # Show first 20
            print(f"  • {file_path}")
        
        if len(stats['modified_files']) > 20:
            print(f"  ... and {len(stats['modified_files']) - 20} more files")
    
    print()
    print("="*70)
    print("  ✅ Rebranding complete!")
    print("="*70)


if __name__ == "__main__":
    stats = rebrand_project()
    print_summary(stats)
