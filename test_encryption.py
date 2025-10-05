#!/usr/bin/env python3

"""
Test script for encryption utilities.
"""

import os
import tempfile
from encryption_utils import (
    encrypt_data, decrypt_data, is_encrypted,
    encrypt_file, decrypt_file, read_file_auto_decrypt
)


def test_basic_encryption():
    """Test basic encryption and decryption."""
    print("Test 1: Basic encryption/decryption")
    print("-" * 50)
    
    original_data = "This is a test share: academic academic academic academic"
    password = "test_password_123"
    
    # Encrypt
    encrypted = encrypt_data(original_data, password)
    print(f"✅ Encrypted data length: {len(encrypted)} bytes")
    print(f"✅ Is encrypted: {is_encrypted(encrypted)}")
    
    # Decrypt with correct password
    decrypted = decrypt_data(encrypted, password)
    print(f"✅ Decrypted data: {decrypted[:50]}...")
    
    assert decrypted == original_data, "Decryption failed!"
    print("✅ Test passed: Data matches after encryption/decryption\n")


def test_wrong_password():
    """Test decryption with wrong password."""
    print("Test 2: Wrong password handling")
    print("-" * 50)
    
    original_data = "secret data"
    correct_password = "correct_pass"
    wrong_password = "wrong_pass"
    
    encrypted = encrypt_data(original_data, correct_password)
    
    try:
        decrypt_data(encrypted, wrong_password)
        print("❌ Test failed: Should have raised ValueError")
        assert False, "Should have raised error"
    except ValueError as e:
        print(f"✅ Correctly rejected wrong password: {e}\n")


def test_file_encryption():
    """Test file encryption/decryption."""
    print("Test 3: File encryption")
    print("-" * 50)
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        test_file = f.name
        test_data = "academic academic abandon abandon about above absent absorb"
        f.write(test_data)
    
    try:
        password = "file_password_456"
        
        # Encrypt file
        encrypt_file(test_file, password)
        print(f"✅ File encrypted: {test_file}")
        
        # Check if encrypted
        with open(test_file, 'rb') as f:
            file_data = f.read()
        print(f"✅ Is encrypted: {is_encrypted(file_data)}")
        
        # Decrypt file
        decrypted = decrypt_file(test_file, password)
        print(f"✅ Decrypted: {decrypted[:40]}...")
        
        assert decrypted == test_data, "File decryption failed!"
        print("✅ Test passed: File encryption/decryption works\n")
        
    finally:
        os.unlink(test_file)


def test_backward_compatibility():
    """Test reading unencrypted files."""
    print("Test 4: Backward compatibility (unencrypted files)")
    print("-" * 50)
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        test_file = f.name
        plain_data = "plain text share data"
        f.write(plain_data)
    
    try:
        # Try to read as plain text
        content = read_file_auto_decrypt(test_file)
        print(f"✅ Read plain file: {content}")
        
        assert content == plain_data, "Plain file reading failed!"
        print("✅ Test passed: Can read unencrypted files\n")
        
    finally:
        os.unlink(test_file)


def test_different_passwords():
    """Test that different passwords produce different ciphertexts."""
    print("Test 5: Different passwords produce different ciphertexts")
    print("-" * 50)
    
    data = "same data for both"
    pass1 = "password1"
    pass2 = "password2"
    
    enc1 = encrypt_data(data, pass1)
    enc2 = encrypt_data(data, pass2)
    
    assert enc1 != enc2, "Different passwords should produce different ciphertexts!"
    print("✅ Test passed: Different passwords produce different outputs\n")


def test_salt_randomization():
    """Test that encryption with same password produces different ciphertexts (due to random salt/IV)."""
    print("Test 6: Salt randomization")
    print("-" * 50)
    
    data = "test data"
    password = "same_password"
    
    enc1 = encrypt_data(data, password)
    enc2 = encrypt_data(data, password)
    
    # Should be different because of random salt and IV
    assert enc1 != enc2, "Same password should produce different ciphertexts due to random salt/IV!"
    
    # But both should decrypt correctly
    dec1 = decrypt_data(enc1, password)
    dec2 = decrypt_data(enc2, password)
    
    assert dec1 == data and dec2 == data, "Both should decrypt to same data!"
    print("✅ Test passed: Random salt/IV ensures different ciphertexts\n")


if __name__ == "__main__":
    print("=" * 50)
    print("Running Encryption Tests")
    print("=" * 50)
    print()
    
    try:
        test_basic_encryption()
        test_wrong_password()
        test_file_encryption()
        test_backward_compatibility()
        test_different_passwords()
        test_salt_randomization()
        
        print("=" * 50)
        print("✅ All tests passed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)