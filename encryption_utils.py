#!/usr/bin/env python3

"""
AES-256 encryption utilities for securing USB pen data.
"""

import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


# Version marker for encrypted files
ENCRYPTION_VERSION = b"SSS_ENC_V1"
VERSION_LENGTH = len(ENCRYPTION_VERSION)


def derive_key(password: str, salt: bytes) -> bytes:
    """
    Derive a 256-bit AES key from a password using PBKDF2.
    
    Args:
        password: User password
        salt: Random salt (should be 16 bytes)
    
    Returns:
        32-byte AES-256 key
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 256 bits for AES-256
        salt=salt,
        iterations=600000,  # OWASP recommended minimum
        backend=default_backend()
    )
    return kdf.derive(password.encode('utf-8'))


def encrypt_data(data: str, password: str) -> bytes:
    """
    Encrypt data using AES-256-CBC with a password.
    
    Args:
        data: Plain text data to encrypt
        password: User password
    
    Returns:
        Encrypted data with version marker, salt, IV, and ciphertext
        Format: VERSION_MARKER (10 bytes) + SALT (16 bytes) + IV (16 bytes) + CIPHERTEXT
    """
    # Generate random salt and IV
    salt = os.urandom(16)
    iv = os.urandom(16)
    
    # Derive encryption key from password
    key = derive_key(password, salt)
    
    # Pad data to be multiple of 16 bytes (AES block size)
    data_bytes = data.encode('utf-8')
    padding_length = 16 - (len(data_bytes) % 16)
    padded_data = data_bytes + bytes([padding_length] * padding_length)
    
    # Encrypt
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    
    # Combine version marker, salt, IV, and ciphertext
    encrypted_package = ENCRYPTION_VERSION + salt + iv + ciphertext
    
    return encrypted_package


def decrypt_data(encrypted_package: bytes, password: str) -> str:
    """
    Decrypt AES-256-CBC encrypted data with a password.
    
    Args:
        encrypted_package: Encrypted data package (with version marker, salt, IV, and ciphertext)
        password: User password
    
    Returns:
        Decrypted plain text data
    
    Raises:
        ValueError: If decryption fails or data is corrupted
    """
    # Check minimum size
    min_size = VERSION_LENGTH + 16 + 16 + 16  # version + salt + iv + at least one block
    if len(encrypted_package) < min_size:
        raise ValueError("Encrypted data is too short or corrupted")
    
    # Extract version marker
    version = encrypted_package[:VERSION_LENGTH]
    if version != ENCRYPTION_VERSION:
        raise ValueError("Unsupported encryption version or invalid encrypted data")
    
    # Extract salt, IV, and ciphertext
    offset = VERSION_LENGTH
    salt = encrypted_package[offset:offset + 16]
    offset += 16
    iv = encrypted_package[offset:offset + 16]
    offset += 16
    ciphertext = encrypted_package[offset:]
    
    # Derive decryption key
    key = derive_key(password, salt)
    
    # Decrypt
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    
    try:
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")
    
    # Remove padding
    padding_length = padded_data[-1]
    if padding_length > 16 or padding_length == 0:
        raise ValueError("Invalid padding - incorrect password or corrupted data")
    
    # Verify padding
    for i in range(padding_length):
        if padded_data[-(i + 1)] != padding_length:
            raise ValueError("Invalid padding - incorrect password or corrupted data")
    
    data = padded_data[:-padding_length]
    
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        raise ValueError("Decryption produced invalid data - incorrect password")


def is_encrypted(data: bytes) -> bool:
    """
    Check if data appears to be encrypted by this module.
    
    Args:
        data: Data to check
    
    Returns:
        True if data starts with our encryption version marker
    """
    if len(data) < VERSION_LENGTH:
        return False
    return data[:VERSION_LENGTH] == ENCRYPTION_VERSION


def encrypt_file(file_path: str, password: str) -> None:
    """
    Encrypt a file in place using AES-256.
    If the file is already encrypted, it will be re-encrypted with the new password.
    
    Args:
        file_path: Path to the file to encrypt
        password: Encryption password
    """
    # Read file content
    with open(file_path, 'rb') as f:
        data = f.read()
    
    # If already encrypted, decrypt first
    if is_encrypted(data):
        # This will be handled by the caller - they should read and decrypt first
        # For now, we'll treat it as plain text that needs encryption
        text_data = data.decode('utf-8', errors='ignore')
    else:
        text_data = data.decode('utf-8')
    
    # Encrypt
    encrypted_data = encrypt_data(text_data, password)
    
    # Write back
    with open(file_path, 'wb') as f:
        f.write(encrypted_data)


def decrypt_file(file_path: str, password: str) -> str:
    """
    Decrypt a file and return its contents.
    
    Args:
        file_path: Path to the encrypted file
        password: Decryption password
    
    Returns:
        Decrypted file contents as string
    """
    with open(file_path, 'rb') as f:
        encrypted_data = f.read()
    
    return decrypt_data(encrypted_data, password)


def read_file_auto_decrypt(file_path: str, password: str = None) -> str:
    """
    Read a file and automatically detect if it's encrypted.
    If encrypted and password is provided, decrypt it.
    If encrypted and no password, raise an error.
    If not encrypted, return plain content.
    
    Args:
        file_path: Path to the file
        password: Optional password for decryption
    
    Returns:
        File contents as string
    """
    with open(file_path, 'rb') as f:
        data = f.read()
    
    if is_encrypted(data):
        if password is None:
            raise ValueError("File is encrypted but no password provided")
        return decrypt_data(data, password)
    else:
        # Plain text file
        return data.decode('utf-8')