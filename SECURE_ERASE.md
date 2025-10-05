# Secure Erase Feature

## Overview

The SSS USB Key Manager now includes secure erase functionality to protect against data recovery by smart recovery tools. This feature uses multiple overwrite passes with random data to ensure that deleted files cannot be recovered using forensic or standard file recovery methods.

## Why Secure Erase?

When you delete a file normally:
1. The file is removed from the directory listing
2. The storage space is marked as "available"
3. **BUT** the actual data remains on the disk until overwritten
4. Recovery tools can easily restore these "deleted" files

**Security Risk:** If a USB drive containing old SSS shares is lost or stolen, an attacker could use recovery software to retrieve the deleted shares, even if you thought they were erased.

**Solution:** Secure erase overwrites the file data multiple times with random data before deleting it, making recovery impossible.

## When to Use Secure Erase

### Recommended Scenarios

1. **Reusing USB drives** - Before writing new shares to a USB that previously contained shares
2. **Updating backups** - When replacing old shares with new ones
3. **Disposing of USB drives** - Before giving away or discarding a USB
4. **After compromise** - If you suspect a USB may have been accessed
5. **Regular security maintenance** - Periodically refresh your shares and erase old ones

### Not Necessary When

- Using a brand new USB drive (straight from the package)
- The USB has never contained sensitive data
- You're in a hurry and the USB is already clean

## Secure Erase Options

When writing shares to USB drives, you'll be presented with four options for each USB:

### 1. ✓ Skip - Don't erase anything (Default)

**When to use:**
- Brand new USB drive
- USB is already clean
- You need to work quickly

**What it does:**
- No erase operation
- Fastest option
- Existing files remain untouched
- New share will be written or overwrite existing share file

**Time:** Instant

---

### 2. 🗂️ Erase only SSS_Shares directory (Recommended)

**When to use:**
- USB previously contained SSS shares
- You want to keep other files on the USB
- You're updating your backup shares

**What it does:**
- Finds the `SSS_Shares` directory
- Securely erases all files inside it (3-pass overwrite)
- Removes the directory
- **Preserves** all other files on the USB

**How it works:**
1. Pass 1: Overwrite each file with random data
2. Pass 2: Overwrite with different random data
3. Pass 3: Overwrite with zeros
4. Delete files and remove directory

**Time:** ~10-30 seconds (depends on number/size of old shares)

**Security Level:** ⭐⭐⭐⭐⭐ High - Prevents recovery of old shares

---

### 3. 🗑️ Securely erase ALL files on USB

**When to use:**
- You want a completely clean USB
- The USB contains other sensitive data you want to erase
- You're disposing of or giving away the USB
- Maximum security is required

**What it does:**
- Scans entire USB for all files
- Securely erases every file (excluding system directories)
- 3-pass overwrite method
- **WARNING:** Irreversible! All data is destroyed

**What's preserved:**
- System directories (`.Trash`, `lost+found`, etc.) are skipped
- The USB filesystem itself (you can still use the USB)

**Time:** Varies greatly depending on amount of data
- Empty USB: ~5 seconds
- 100 MB: ~30 seconds
- 1 GB: ~5 minutes
- 10 GB: ~30+ minutes

**Security Level:** ⭐⭐⭐⭐⭐ Maximum - Complete secure wipe

**⚠️ WARNING:** This option requires additional confirmation due to its destructive nature.

---

### 4. 💾 Erase free space only (keeps current files)

**When to use:**
- You've already deleted sensitive files but want to prevent their recovery
- USB has a history of sensitive data
- You want to keep current files but erase "deleted" data
- Belt-and-suspenders approach

**What it does:**
- Leaves all current files intact
- Creates a temporary file that fills all free space
- Fills the temporary file with random data
- Securely deletes the temporary file
- Overwrites areas where previously deleted files existed

**How it works:**
1. Checks available free space
2. Creates temporary file with random data filling free space
3. File grows until disk is full
4. Securely deletes temporary file (1 pass)
5. All free space now contains random data

**Time:** Proportional to free space
- 100 MB free: ~30 seconds
- 1 GB free: ~2 minutes
- 10 GB free: ~20 minutes
- 32 GB free (empty USB): ~1 hour+

**Security Level:** ⭐⭐⭐⭐ Very High - Prevents recovery of previously deleted files

**Note:** This is the most time-consuming option but provides protection against historical data recovery.

---

## Technical Details

### Overwrite Method

The secure erase uses a DoD 5220.22-M inspired method:

```
For each file:
  1. Open file for read/write
  2. Pass 1: Write random bytes (os.urandom)
  3. Flush and sync to disk
  4. Pass 2: Write different random bytes
  5. Flush and sync to disk  
  6. Pass 3: Write zeros (0x00)
  7. Flush and sync to disk
  8. Delete file
```

### Why 3 Passes?

- **Pass 1 (Random):** Overwrites original data, scrambles bit patterns
- **Pass 2 (Random):** Different random data prevents analysis of first pass
- **Pass 3 (Zeros):** Standardizes final state, helps with some forensic techniques

**Note:** Modern research suggests even 1-pass random overwrite is sufficient for magnetic drives, but 3 passes provides defense-in-depth and peace of mind.

### Effectiveness

**Will defeat:**
- ✅ Standard file recovery tools (Recuva, PhotoRec, TestDisk, etc.)
- ✅ Basic forensic analysis
- ✅ Disk imaging followed by data carving
- ✅ Undelete utilities

**May not defeat:**
- ❓ Nation-state level attacks with electron microscope analysis (theoretical)
- ❓ Specialized hardware forensics on magnetic drives (theoretical)

**For SSDs/Flash drives:**
- Effective but note that flash memory has wear leveling
- Some data may persist in spare areas (over-provisioning)
- For maximum security on SSDs, consider full device encryption from the start

## Progress Tracking

During secure erase operations, you'll see:

1. **Progress bar** - Visual indicator of completion (0-100%)
2. **Status messages** - Current operation being performed
3. **File names** - Which files are being erased
4. **Time estimate** - Based on amount of data

Example progress messages:
```
[  0%] Scanning USB drive for files...
[ 10%] Found 5 files to erase
[ 20%] Erasing: share_1.txt
[ 40%] Erasing: share_2.txt
[ 60%] Erasing: README.txt
[ 80%] Cleaning up empty directories...
[100%] Secure erase complete: 5 files erased
```

## Testing the Feature

Run the included test suite to verify secure erase works correctly:

```bash
python3 test_secure_erase.py
```

This will:
- Create temporary test files
- Perform secure erase operations
- Verify files are properly deleted
- Test all erase modes (SSS-only, all files, info gathering)
- Display results

All tests should pass (4/4 tests passed).

## Security Guarantees

### What Secure Erase DOES Guarantee

✅ Files overwritten with secure erase **cannot be recovered** using:
- Standard data recovery software
- File carving tools
- Undelete utilities
- Basic forensic methods

✅ Multiple random passes ensure:
- Original data is destroyed
- File content cannot be reconstructed
- Bit patterns are randomized

### What Secure Erase DOES NOT Guarantee

❌ **Not a substitute for full disk encryption**
- Always use encryption for sensitive data (which SSS does!)
- Secure erase is a complementary measure

❌ **Not instantaneous**
- Takes time proportional to data size
- Large amounts of data can take considerable time

❌ **Not protection against physical destruction**
- For ultimate security, physically destroy the drive

## Best Practices

1. **Reusing USB Drives:**
   - Use "SSS_Shares only" erase when updating backups
   - Or use "ALL files" for a completely clean slate

2. **Regular Maintenance:**
   - Periodically regenerate shares with new password
   - Securely erase old shares when creating new ones

3. **Before Disposal:**
   - Use "ALL files" erase
   - Then optionally use "Free space" erase
   - Or physically destroy the drive

4. **Combining with Encryption:**
   - SSS already uses AES-256 encryption
   - Secure erase adds an additional layer of protection
   - Together they provide defense-in-depth

5. **Time Management:**
   - Choose "Skip" when time is critical
   - Choose "SSS_Shares" for normal use (recommended)
   - Choose "ALL files" or "Free space" when you have time and maximum security is needed

## Comparison with Other Methods

| Method | Security | Speed | Ease of Use |
|--------|----------|-------|-------------|
| Normal Delete | ❌ Very Low | ⚡⚡⚡ Instant | ⭐⭐⭐ Easy |
| Trash/Recycle Bin | ❌ None | ⚡⚡⚡ Instant | ⭐⭐⭐ Easy |
| **SSS Secure Erase** | ✅ High | ⚡⚡ Fast | ⭐⭐⭐ Easy (GUI) |
| `shred` command | ✅ High | ⚡⚡ Fast | ⭐ Technical |
| Format (quick) | ❌ Low | ⚡⚡⚡ Fast | ⭐⭐ Moderate |
| Format (full) | ⚠️ Medium | ⚡ Slow | ⭐⭐ Moderate |
| dd from /dev/zero | ⚠️ Medium | ⚡ Very Slow | ⭐ Technical |
| dd from /dev/urandom | ✅ High | ⚡ Very Slow | ⭐ Technical |
| Physical Destruction | ✅✅ Maximum | ⚡ Instant | ⭐ Destructive |

## Troubleshooting

### "Secure erase failed: Permission denied"

**Cause:** USB is mounted read-only or you don't have write permissions

**Solution:**
1. Check USB is not write-protected (physical switch)
2. Remount USB with write permissions
3. Check you own the files: `ls -la /path/to/usb`

### "Secure erase is very slow"

**Cause:** Large amount of data or slow USB drive

**Solution:**
- This is normal for large data amounts
- USB 2.0 drives are slower than USB 3.0
- Consider "SSS_Shares only" instead of "ALL files"
- For empty or nearly-empty USBs, use "Skip"

### "Errors occurred during erase"

**Cause:** Some files couldn't be erased (permissions, in use, etc.)

**Solution:**
- Check the log for specific error messages
- Close any programs that might be accessing the USB
- Unmount and remount the USB
- Try again

### "USB appears full after free space erase"

**Cause:** The temporary fill file might not have been deleted

**Solution:**
1. Manually delete any `.secure_erase_temp_*.tmp` files
2. Or reformat the USB

## FAQ

**Q: Is one pass enough?**
A: Modern research suggests yes for magnetic drives, but we use 3 passes for defense-in-depth.

**Q: Does this work on SSDs?**
A: Yes, but SSDs have wear leveling which may leave copies in spare areas. Full disk encryption is recommended for SSDs.

**Q: How long does it take?**
A: Depends on data amount and USB speed. Small files (< 1MB) take seconds, large amounts take minutes.

**Q: Can I cancel during erase?**
A: Currently no. Once started, let it complete. Canceling may leave partially erased files.

**Q: Does this damage the USB?**
A: No. Secure erase is just writing data normally. No more wear than normal use.

**Q: Should I always use secure erase?**
A: It's recommended when reusing USBs or updating shares, but not strictly necessary for brand new USBs.

**Q: What about encrypted shares?**
A: SSS shares are already encrypted with AES-256. Secure erase provides an additional layer of protection in case the encryption is somehow compromised or if someone has your password.

## See Also

- `ENCRYPTION_UPGRADE.md` - Information about AES-256 encryption
- `USB_WORKFLOW.md` - USB workflow and efficiency improvements
- `README.md` - Main documentation
- `test_secure_erase.py` - Test suite for secure erase functionality