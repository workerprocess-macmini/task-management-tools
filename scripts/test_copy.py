#!/usr/bin/env python3
"""
Test script: Copy and test file operations
"""

import os
import shutil
import json
from datetime import datetime

def create_test_file():
    """Create a test file"""
    test_data = {
        "test_id": "test-copy-001",
        "timestamp": datetime.now().isoformat(),
        "message": "This is a test file for git workflow",
        "status": "success"
    }
    
    test_file = "test_data.json"
    with open(test_file, 'w') as f:
        json.dump(test_data, f, indent=2)
    
    print(f"✅ Created test file: {test_file}")
    return test_file

def copy_test_file(source, destination):
    """Copy test file to destination"""
    try:
        shutil.copy(source, destination)
        print(f"✅ Copied: {source} → {destination}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def verify_copy(destination):
    """Verify copied file"""
    if os.path.exists(destination):
        with open(destination, 'r') as f:
            data = json.load(f)
        print(f"✅ Verified: {destination}")
        print(f"   Content: {data}")
        return True
    else:
        print(f"❌ File not found: {destination}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Test: Copy File Operations")
    print("=" * 50)
    
    # Step 1: Create test file
    test_file = create_test_file()
    
    # Step 2: Copy to backup
    backup_file = f"{test_file}.backup"
    copy_success = copy_test_file(test_file, backup_file)
    
    # Step 3: Verify backup
    if copy_success:
        verify_copy(backup_file)
    
    # Step 4: Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"✅ Cleaned up: {test_file}")
    
    if os.path.exists(backup_file):
        os.remove(backup_file)
        print(f"✅ Cleaned up: {backup_file}")
    
    print("=" * 50)
    print("✅ Test completed successfully!")
    print("=" * 50)
