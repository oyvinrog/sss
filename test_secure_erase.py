#!/usr/bin/env python3
"""
Test script for secure erase functionality.
Creates test files and verifies they are securely erased.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from secure_erase_utils import (
    secure_erase_file, 
    secure_erase_usb, 
    get_usb_info,
    SecureEraseProgress
)


def create_test_environment(base_path):
    """Create test files and directories."""
    print(f"Creating test environment in: {base_path}")
    
    # Create SSS_Shares directory with test files
    sss_dir = Path(base_path) / "SSS_Shares"
    sss_dir.mkdir(exist_ok=True)
    
    # Create test share files
    for i in range(1, 4):
        share_file = sss_dir / f"share_{i}.txt"
        with open(share_file, 'w') as f:
            f.write(f"Test share {i}\n" * 1000)  # Create some content
            f.write("SENSITIVE DATA THAT SHOULD BE ERASED\n" * 100)
        print(f"  Created: {share_file}")
    
    # Create README
    readme_file = sss_dir / "README.txt"
    with open(readme_file, 'w') as f:
        f.write("SSS Test Share\n")
    print(f"  Created: {readme_file}")
    
    # Create some other files outside SSS_Shares
    other_file = Path(base_path) / "other_file.txt"
    with open(other_file, 'w') as f:
        f.write("Other file content\n" * 500)
    print(f"  Created: {other_file}")
    
    return sss_dir, other_file


def test_file_erase():
    """Test secure erasure of a single file."""
    print("\n" + "="*60)
    print("TEST 1: Single File Secure Erase")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test file
        test_file = Path(tmpdir) / "test_file.txt"
        with open(test_file, 'w') as f:
            f.write("SENSITIVE DATA\n" * 1000)
        
        file_size = test_file.stat().st_size
        print(f"Created test file: {test_file}")
        print(f"File size: {file_size} bytes")
        
        # Secure erase
        print("Performing secure erase (3 passes)...")
        secure_erase_file(test_file, passes=3)
        
        # Verify file is gone
        if test_file.exists():
            print("❌ FAILED: File still exists!")
            return False
        else:
            print("✅ PASSED: File successfully erased")
            return True


def test_sss_directory_erase():
    """Test secure erasure of SSS_Shares directory only."""
    print("\n" + "="*60)
    print("TEST 2: SSS_Shares Directory Secure Erase")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test environment
        sss_dir, other_file = create_test_environment(tmpdir)
        
        # Count files before
        sss_files_before = len(list(sss_dir.rglob('*')))
        print(f"\nFiles in SSS_Shares before: {sss_files_before}")
        print(f"Other file exists: {other_file.exists()}")
        
        # Progress callback
        def progress_callback(percent, message):
            print(f"  [{percent:3d}%] {message}")
        
        progress = SecureEraseProgress(progress_callback)
        
        # Secure erase SSS_Shares only
        print("\nPerforming secure erase of SSS_Shares directory...")
        files_erased, errors = secure_erase_usb(tmpdir, progress, erase_all=False)
        
        print(f"\nFiles erased: {files_erased}")
        print(f"Errors: {errors}")
        
        # Verify SSS_Shares is gone
        sss_exists = sss_dir.exists()
        other_exists = other_file.exists()
        
        print(f"\nSSS_Shares exists after erase: {sss_exists}")
        print(f"Other file exists after erase: {other_exists}")
        
        if not sss_exists and other_exists and files_erased > 0:
            print("✅ PASSED: SSS_Shares erased, other files preserved")
            return True
        else:
            print("❌ FAILED: Unexpected result")
            return False


def test_full_erase():
    """Test secure erasure of all files."""
    print("\n" + "="*60)
    print("TEST 3: Full USB Secure Erase")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test environment
        sss_dir, other_file = create_test_environment(tmpdir)
        
        # Count files before
        all_files_before = len([f for f in Path(tmpdir).rglob('*') if f.is_file()])
        print(f"\nTotal files before: {all_files_before}")
        
        # Progress callback
        def progress_callback(percent, message):
            print(f"  [{percent:3d}%] {message}")
        
        progress = SecureEraseProgress(progress_callback)
        
        # Secure erase all files
        print("\nPerforming secure erase of all files...")
        files_erased, errors = secure_erase_usb(tmpdir, progress, erase_all=True)
        
        print(f"\nFiles erased: {files_erased}")
        print(f"Errors: {errors}")
        
        # Count files after
        all_files_after = len([f for f in Path(tmpdir).rglob('*') if f.is_file()])
        print(f"Total files after: {all_files_after}")
        
        # Verify all files are gone
        sss_exists = sss_dir.exists()
        other_exists = other_file.exists()
        
        print(f"\nSSS_Shares exists after erase: {sss_exists}")
        print(f"Other file exists after erase: {other_exists}")
        
        if all_files_after == 0 and files_erased > 0:
            print("✅ PASSED: All files securely erased")
            return True
        else:
            print("❌ FAILED: Some files remain")
            return False


def test_usb_info():
    """Test USB info gathering."""
    print("\n" + "="*60)
    print("TEST 4: USB Info Gathering")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test environment
        sss_dir, other_file = create_test_environment(tmpdir)
        
        # Get USB info
        print("\nGathering USB info...")
        info = get_usb_info(tmpdir)
        
        print(f"  Path: {info['path']}")
        print(f"  Name: {info['name']}")
        print(f"  Total size: {info['total_gb']:.2f} GB")
        print(f"  Used: {info['used_gb']:.2f} GB")
        print(f"  Free: {info['free_gb']:.2f} GB")
        print(f"  File count: {info['file_count']}")
        print(f"  Has SSS shares: {info['has_sss_shares']}")
        print(f"  SSS file count: {info['sss_file_count']}")
        
        # Verify info
        if info['has_sss_shares'] and info['sss_file_count'] == 4 and info['file_count'] == 5:
            print("✅ PASSED: USB info correctly gathered")
            return True
        else:
            print("❌ FAILED: Incorrect USB info")
            return False


def main():
    """Run all tests."""
    print("="*60)
    print("SECURE ERASE UTILITY TEST SUITE")
    print("="*60)
    
    tests = [
        ("Single File Erase", test_file_erase),
        ("SSS Directory Erase", test_sss_directory_erase),
        ("Full USB Erase", test_full_erase),
        ("USB Info Gathering", test_usb_info),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed_count = 0
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
        if passed:
            passed_count += 1
    
    print("\n" + "="*60)
    print(f"Total: {passed_count}/{len(results)} tests passed")
    print("="*60)
    
    return 0 if passed_count == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())