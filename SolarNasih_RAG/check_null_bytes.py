#!/usr/bin/env python3
"""
Script to detect null bytes in Python files
"""

import os
import sys
from pathlib import Path

def check_file_for_null_bytes(file_path):
    """Check if a file contains null bytes"""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            
        # Check for null bytes
        if b'\x00' in content:
            null_positions = [i for i, byte in enumerate(content) if byte == 0]
            print(f"❌ Found null bytes in {file_path}")
            print(f"   Null bytes at positions: {null_positions[:10]}...")  # Show first 10
            return True
        else:
            print(f"✅ No null bytes found in {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return True

def main():
    """Check all Python files in the current directory and subdirectories"""
    current_dir = Path('.')
    python_files = list(current_dir.rglob('*.py'))
    
    print(f"🔍 Checking {len(python_files)} Python files for null bytes...")
    print()
    
    files_with_null_bytes = []
    
    for file_path in python_files:
        if check_file_for_null_bytes(file_path):
            files_with_null_bytes.append(file_path)
    
    print()
    print("=" * 50)
    
    if files_with_null_bytes:
        print(f"❌ Found {len(files_with_null_bytes)} files with null bytes:")
        for file_path in files_with_null_bytes:
            print(f"   - {file_path}")
        
        print("\n🔧 To fix these files, you can:")
        print("   1. Open each file in a text editor")
        print("   2. Save it with UTF-8 encoding")
        print("   3. Or use: python -c \"open('file.py', 'w', encoding='utf-8').write(open('file.py', 'r', encoding='utf-8').read())\"")
    else:
        print("✅ No files with null bytes found!")

if __name__ == "__main__":
    main() 