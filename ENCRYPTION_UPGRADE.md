# AES-256 Encryption Upgrade

## Overview
This upgrade adds AES-256 encryption with password protection to all USB pen shares. All data written to USB drives is now encrypted, significantly enhancing security.

## What Changed

### New Features
1. **Password-Protected Encryption**: Before splitting or combining keys, users must provide a password
2. **AES-256-CBC Encryption**: Industry-standard encryption for all share files
3. **Secure Key Derivation**: PBKDF2-HMAC-SHA256 with 600,000 iterations
4. **Random Salt & IV**: Each encryption uses unique random values for maximum security
5. **Backward Compatibility**: Automatically detects and encrypts old unencrypted shares

### New Files
- **`encryption_utils.py`**: Core encryption/decryption functionality
  - `encrypt_data()`: Encrypt text data with password
  - `decrypt_data()`: Decrypt encrypted data with password
  - `is_encrypted()`: Check if data is encrypted
  - `read_file_auto_decrypt()`: Automatically detect and decrypt files
  
- **`test_encryption.py`**: Comprehensive test suite for encryption
  - Tests basic encryption/decryption
  - Tests wrong password handling
  - Tests file encryption
  - Tests backward compatibility
  - Tests salt randomization

### Modified Files

#### `requirements.txt`
- Added `cryptography>=41.0.0` for AES-256 encryption support

#### `sss_gui.py`
- Added password input dialog with confirmation
- Modified `start_split()` to prompt for encryption password before splitting
- Modified `start_combine()` to prompt for decryption password before combining
- Updated `write_shares_to_usb()` to encrypt shares before writing
- Updated `read_shares_from_usb()` to decrypt shares when reading
- Added automatic encryption of old unencrypted shares during read operations
- Added detailed logging for encryption operations

#### `README.md`
- Added security section documenting AES-256 encryption
- Updated workflow descriptions to include password steps
- Added encryption technical details
- Added best practices for password management

#### `USB_WORKFLOW.md`
- Added security features section
- Updated split/combine operation workflows
- Documented encryption and decryption processes
- Added password requirements

## Security Specifications

### Encryption Algorithm
- **Cipher**: AES-256-CBC (Advanced Encryption Standard, 256-bit key)
- **Mode**: CBC (Cipher Block Chaining)
- **Block Size**: 16 bytes (128 bits)
- **Key Size**: 32 bytes (256 bits)

### Key Derivation
- **Algorithm**: PBKDF2-HMAC-SHA256
- **Iterations**: 600,000 (OWASP recommended minimum as of 2023)
- **Salt**: 16 random bytes per encryption
- **Output**: 32-byte encryption key

### Encryption Format
Each encrypted file contains:
```
[Version Marker: 10 bytes] + [Salt: 16 bytes] + [IV: 16 bytes] + [Ciphertext: variable]
```

- **Version Marker**: `SSS_ENC_V1` - Identifies encryption version for future compatibility
- **Salt**: Random 16-byte salt for key derivation
- **IV**: Random 16-byte initialization vector for CBC mode
- **Ciphertext**: PKCS#7 padded encrypted data

### Password Requirements
- Minimum: 8 characters (enforced by GUI)
- Recommended: 16+ characters
- Must be remembered - **cannot be recovered if lost**

## User Experience Changes

### Split Operation (Before: 2 steps, After: 3 steps)
1. **NEW**: Enter encryption password (with confirmation)
2. Enter seed phrase
3. Select USB drives for each share

### Combine Operation (Before: 1 step, After: 2 steps)
1. **NEW**: Enter decryption password
2. Select USB drives to read shares

### Additional UI Elements
- Password input dialogs with masked entry
- Password confirmation on split operation
- Clear error messages for incorrect passwords
- Progress indicators showing encryption/decryption status

## Backward Compatibility

The system gracefully handles unencrypted shares from previous versions:

1. **Detection**: Automatically detects if a share file is encrypted or not
2. **Reading**: Can read both encrypted and unencrypted shares
3. **Upgrading**: When an unencrypted share is read, it's automatically encrypted with the current password and saved back to USB
4. **Logging**: Clear messages indicate when old shares are being upgraded

Example:
```
⚠️  Share 1 is NOT encrypted (old format)
ℹ️  Reading plain-text share for backward compatibility
🔄 Encrypting unencrypted share for security...
✅ Share 1 has been encrypted and updated on USB
```

## Testing

Run the encryption test suite:
```bash
python3 test_encryption.py
```

Tests include:
- Basic encryption/decryption
- Wrong password rejection
- File encryption/decryption
- Plain text file reading (backward compatibility)
- Different passwords produce different outputs
- Salt randomization

All tests pass with current implementation.

## Security Considerations

### Strengths
✅ Industry-standard AES-256 encryption
✅ Strong key derivation (600,000 iterations)
✅ Unique salt and IV per encryption
✅ Secure padding (PKCS#7)
✅ No password storage or caching
✅ Clear error messages without information leakage

### Limitations
⚠️ Password cannot be recovered if lost
⚠️ User must remember password for all 5 shares
⚠️ Password not stored anywhere - purely memory-based security
⚠️ Brute force attacks possible if password is weak

### Best Practices
1. Use strong, unique passwords (16+ characters)
2. Store password in secure password manager
3. Consider physical secure storage for password
4. Never store password on any of the USB drives
5. Test recovery process before relying on it
6. Keep USB drives physically secure in separate locations

## Migration Guide

### For Existing Users
1. No action required - backward compatibility maintained
2. When you next read old shares, they'll be automatically encrypted
3. Consider creating new encrypted shares for maximum security:
   - Run split operation with same seed phrase
   - Use strong password
   - Replace old USBs with new encrypted ones

### For New Users
1. Install updated version with `install.sh`
2. All shares automatically encrypted on creation
3. Follow password best practices

## Installation

The encryption functionality requires the `cryptography` library, which is automatically installed via:

```bash
./install.sh
```

Or manually:
```bash
pip install cryptography>=41.0.0
```

## Support

If you encounter issues:
1. Verify `cryptography` library is installed
2. Run `python3 test_encryption.py` to verify encryption works
3. Check logs in GUI output window for detailed error messages
4. Ensure password is entered correctly (case-sensitive)

## Version History

- **v2.0** (2025-10-05): Added AES-256 encryption with password protection
- **v1.0** (2024-10-04): Initial release with unencrypted shares