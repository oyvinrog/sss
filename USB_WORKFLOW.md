# USB Workflow Efficiency Improvements

## Overview
The USB management process has been significantly optimized to make writing/reading 5 USB keys as efficient as possible.

## Key Improvements

### 1. **Automatic USB Detection**
- No more manual browsing through file systems
- Application automatically scans for USB drives every 2 seconds
- Uses multiple detection methods:
  - Checks `/media`, `/mnt`, `/run/media` mount points
  - Parses `lsblk` output for removable devices
  - Monitors `/proc/mounts` for changes

### 2. **Smart Drive Identification**
- **🆕 NEW indicator**: Newly inserted drives are automatically highlighted
- **Drive information**: Shows name, path, size, and free space
- **Auto-selection**: Newly inserted drives are automatically selected

### 3. **Efficient Interaction**
- **One-click selection**: Click a drive and press "Select USB"
- **Double-click selection**: Double-click any drive to select it immediately
- **Auto-refresh**: List updates automatically every 2 seconds
- **Manual refresh**: "Refresh Now" button for immediate update
- **Fallback option**: "Browse..." button for manual directory selection if auto-detection fails

### 4. **Streamlined Process**
For each of the 5 USB pens, the user workflow is:
1. Dialog opens showing available USB drives
2. Insert USB pen (if not already inserted)
3. Wait ~2 seconds for auto-detection (or click refresh)
4. Drive appears with 🆕 NEW indicator and is auto-selected
5. Click "Select USB" or double-click the drive
6. Done! Move to next share

**Time savings**: From ~30-60 seconds per USB (browsing file system) to ~5-10 seconds per USB (single click).

## Technical Details

### USB Detection Methods

#### Method 1: Mount Point Scanning
```python
# Scans common mount directories
/media/username/
/mnt/
/run/media/username/
```

#### Method 2: lsblk Integration
```bash
# Parses removable device information
lsblk -J -o NAME,MOUNTPOINT,RM,SIZE,LABEL
```

#### Method 3: Mount Change Detection
```python
# Compares /proc/mounts before and after insertion
# Highlights new mounts with 🆕 indicator
```

### Auto-Refresh Timer
- Refresh interval: 2 seconds
- Runs until USB is selected or dialog is cancelled
- Maintains current selection during refresh

### Drive Information Display
```
USB_DRIVE_NAME 🆕 NEW
    Path: /media/user/USB_DRIVE_NAME
    Size: 32.0 GB (Free: 28.5 GB)
```

## User Experience Flow

### Split Operation (Writing 5 Shares)
```
1. Enter seed phrase
2. For each of 5 shares:
   a. Dialog opens
   b. Insert USB → Auto-detected → Auto-selected
   c. Click "Select USB"
   d. Share written with progress feedback
3. Success message

Total time: ~2 minutes for all 5 USBs
```

### Combine Operation (Reading 3-5 Shares)
```
1. Choose number of shares (3-5)
2. For each share:
   a. Dialog opens
   b. Insert USB → Auto-detected → Auto-selected
   c. Click "Select USB"
   d. Share read with progress feedback
3. Shares combined and validated
4. Recovered phrase displayed

Total time: ~1-2 minutes for 3 USBs
```

## Smart Share Selection

### Multiple Shares on Same USB
If a USB drive contains multiple share files (e.g., from different backup sessions), the application automatically:
- **Selects the most recent share** based on file modification time
- **Displays all available shares** with timestamps
- **Logs the selection** for transparency

Example output:
```
ℹ️  Found 3 share files, selecting most recent:
   1. share_1.txt (2025-10-04 14:32:15) ✓ SELECTED
   2. share_1.txt (2025-09-15 10:20:30)
   3. share_1.txt (2025-08-01 08:15:00)
```

This ensures you always use the latest backup without manual selection.

## Error Handling
- Graceful fallback if auto-detection fails
- Manual browse option always available
- Clear error messages for invalid drives
- Validation of share files before processing
- Smart handling of multiple shares on same USB

## Compatibility
- Works on all Linux distributions
- Supports standard mount points
- Compatible with any USB filesystem (FAT32, exFAT, ext4, etc.)
- No admin/root privileges required
