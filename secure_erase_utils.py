#!/usr/bin/env python3
"""
Secure erase utilities for USB drives.
Implements secure deletion that prevents recovery by smart recovery tools.
"""

import os
import random
import shutil
from pathlib import Path
from typing import Callable, Optional


class SecureEraseProgress:
    """Callback interface for progress reporting."""
    
    def __init__(self, callback: Optional[Callable[[int, str], None]] = None):
        self.callback = callback
    
    def report(self, percent: int, message: str):
        """Report progress."""
        if self.callback:
            self.callback(percent, message)


def get_files_to_erase(usb_path: str) -> list:
    """
    Get list of all files on USB drive (excluding system files).
    
    Args:
        usb_path: Path to USB mount point
        
    Returns:
        List of Path objects for files to erase
    """
    usb_path_obj = Path(usb_path)
    files_to_erase = []
    
    # Skip system/hidden directories
    skip_dirs = {'.Trash-1000', '.Trash', 'lost+found', 'System Volume Information', '$RECYCLE.BIN'}
    
    for item in usb_path_obj.rglob('*'):
        # Skip if in a system directory
        if any(skip_dir in item.parts for skip_dir in skip_dirs):
            continue
        
        # Only process files
        if item.is_file():
            files_to_erase.append(item)
    
    return files_to_erase


def secure_erase_file(file_path: Path, passes: int = 3) -> None:
    """
    Securely erase a single file using multiple overwrite passes.
    
    Uses DoD 5220.22-M inspired method:
    - Pass 1: Overwrite with random data
    - Pass 2: Overwrite with random data (different)
    - Pass 3: Overwrite with zeros
    - Then delete the file
    
    Args:
        file_path: Path to file to erase
        passes: Number of overwrite passes (default 3)
    """
    if not file_path.exists():
        return
    
    try:
        file_size = file_path.stat().st_size
        
        # Perform overwrite passes
        with open(file_path, 'rb+') as f:
            for pass_num in range(passes):
                f.seek(0)
                
                if pass_num < passes - 1:
                    # Random data passes
                    chunk_size = 64 * 1024  # 64KB chunks
                    remaining = file_size
                    
                    while remaining > 0:
                        chunk = min(chunk_size, remaining)
                        random_data = os.urandom(chunk)
                        f.write(random_data)
                        remaining -= chunk
                else:
                    # Final pass: zeros
                    f.write(b'\x00' * file_size)
                
                f.flush()
                os.fsync(f.fileno())
        
        # Delete the file
        file_path.unlink()
        
    except Exception as e:
        raise RuntimeError(f"Failed to securely erase {file_path}: {e}")


def secure_erase_directory(dir_path: Path) -> None:
    """
    Securely erase a directory and all its contents.
    
    Args:
        dir_path: Path to directory to erase
    """
    if not dir_path.exists() or not dir_path.is_dir():
        return
    
    # First, securely erase all files in the directory
    for item in dir_path.rglob('*'):
        if item.is_file():
            secure_erase_file(item, passes=3)
    
    # Then remove empty directories
    try:
        shutil.rmtree(dir_path, ignore_errors=True)
    except Exception:
        pass


def secure_erase_usb(
    usb_path: str, 
    progress: Optional[SecureEraseProgress] = None,
    erase_all: bool = False
) -> tuple[int, int]:
    """
    Securely erase files on USB drive.
    
    Args:
        usb_path: Path to USB mount point
        progress: Progress callback object
        erase_all: If True, erase all files. If False, only erase SSS_Shares directory
        
    Returns:
        Tuple of (files_erased, errors_encountered)
    """
    if progress is None:
        progress = SecureEraseProgress()
    
    usb_path_obj = Path(usb_path)
    
    if not usb_path_obj.exists():
        raise ValueError(f"USB path does not exist: {usb_path}")
    
    files_erased = 0
    errors = 0
    
    if erase_all:
        # Erase all files on USB (excluding system directories)
        progress.report(0, "Scanning USB drive for files...")
        files_to_erase = get_files_to_erase(usb_path)
        
        if not files_to_erase:
            progress.report(100, "No files to erase")
            return 0, 0
        
        progress.report(10, f"Found {len(files_to_erase)} files to erase")
        
        total_files = len(files_to_erase)
        for idx, file_path in enumerate(files_to_erase):
            try:
                percent = 10 + int((idx / total_files) * 80)
                progress.report(percent, f"Erasing: {file_path.name}")
                secure_erase_file(file_path, passes=3)
                files_erased += 1
            except Exception as e:
                errors += 1
                progress.report(percent, f"Error erasing {file_path.name}: {e}")
        
        # Clean up empty directories
        progress.report(90, "Cleaning up empty directories...")
        for item in sorted(usb_path_obj.rglob('*'), key=lambda p: -len(p.parts)):
            if item.is_dir() and not any(item.iterdir()):
                try:
                    item.rmdir()
                except Exception:
                    pass
        
        progress.report(100, f"Secure erase complete: {files_erased} files erased")
        
    else:
        # Only erase SSS_Shares directory
        sss_dir = usb_path_obj / "SSS_Shares"
        
        if not sss_dir.exists():
            progress.report(100, "No SSS_Shares directory found")
            return 0, 0
        
        progress.report(10, "Found SSS_Shares directory")
        
        # Count files first
        files_to_erase = [f for f in sss_dir.rglob('*') if f.is_file()]
        total_files = len(files_to_erase)
        
        if total_files == 0:
            progress.report(100, "SSS_Shares directory is empty")
            sss_dir.rmdir()
            return 0, 0
        
        progress.report(20, f"Found {total_files} files in SSS_Shares")
        
        for idx, file_path in enumerate(files_to_erase):
            try:
                percent = 20 + int((idx / total_files) * 70)
                progress.report(percent, f"Erasing: {file_path.name}")
                secure_erase_file(file_path, passes=3)
                files_erased += 1
            except Exception as e:
                errors += 1
                progress.report(percent, f"Error erasing {file_path.name}: {e}")
        
        # Remove the directory
        progress.report(90, "Removing SSS_Shares directory...")
        try:
            shutil.rmtree(sss_dir, ignore_errors=True)
        except Exception:
            pass
        
        progress.report(100, f"Secure erase complete: {files_erased} files erased")
    
    return files_erased, errors


def quick_erase_usb_free_space(usb_path: str, progress: Optional[SecureEraseProgress] = None) -> None:
    """
    Overwrite free space on USB drive to prevent recovery of previously deleted files.
    
    This creates a large temporary file filled with random data to occupy all free space,
    then securely deletes it.
    
    Args:
        usb_path: Path to USB mount point
        progress: Progress callback object
    """
    if progress is None:
        progress = SecureEraseProgress()
    
    usb_path_obj = Path(usb_path)
    
    if not usb_path_obj.exists():
        raise ValueError(f"USB path does not exist: {usb_path}")
    
    progress.report(0, "Checking available space...")
    
    # Get available space
    stat = os.statvfs(usb_path)
    free_bytes = stat.f_bavail * stat.f_frsize
    
    if free_bytes < 1024 * 1024:  # Less than 1MB
        progress.report(100, "No significant free space to erase")
        return
    
    free_mb = free_bytes / (1024 * 1024)
    progress.report(10, f"Erasing {free_mb:.1f} MB of free space...")
    
    # Create temporary file to fill free space
    temp_file = usb_path_obj / f".secure_erase_temp_{os.getpid()}.tmp"
    
    try:
        chunk_size = 1024 * 1024  # 1MB chunks
        written = 0
        
        with open(temp_file, 'wb') as f:
            while written < free_bytes:
                try:
                    # Write random data
                    chunk = min(chunk_size, free_bytes - written)
                    f.write(os.urandom(chunk))
                    written += chunk
                    
                    percent = 10 + int((written / free_bytes) * 70)
                    progress.report(percent, f"Writing random data: {written / (1024*1024):.1f} MB")
                    
                except IOError:
                    # Disk full - expected behavior
                    break
        
        progress.report(80, "Securely deleting temporary file...")
        
        # Securely delete the temporary file
        secure_erase_file(temp_file, passes=1)
        
        progress.report(100, "Free space erasure complete")
        
    except Exception as e:
        # Clean up temp file if it exists
        if temp_file.exists():
            try:
                temp_file.unlink()
            except Exception:
                pass
        raise RuntimeError(f"Failed to erase free space: {e}")


def get_usb_info(usb_path: str) -> dict:
    """
    Get information about USB drive.
    
    Args:
        usb_path: Path to USB mount point
        
    Returns:
        Dictionary with USB information
    """
    usb_path_obj = Path(usb_path)
    
    if not usb_path_obj.exists():
        raise ValueError(f"USB path does not exist: {usb_path}")
    
    # Get filesystem stats
    stat = os.statvfs(usb_path)
    total_bytes = stat.f_blocks * stat.f_frsize
    free_bytes = stat.f_bavail * stat.f_frsize
    used_bytes = total_bytes - free_bytes
    
    # Count files
    files = get_files_to_erase(usb_path)
    file_count = len(files)
    
    # Check for SSS directory
    sss_dir = usb_path_obj / "SSS_Shares"
    has_sss = sss_dir.exists()
    sss_files = 0
    if has_sss:
        sss_files = len([f for f in sss_dir.rglob('*') if f.is_file()])
    
    return {
        'path': usb_path,
        'name': os.path.basename(usb_path),
        'total_bytes': total_bytes,
        'used_bytes': used_bytes,
        'free_bytes': free_bytes,
        'total_gb': total_bytes / (1024**3),
        'used_gb': used_bytes / (1024**3),
        'free_gb': free_bytes / (1024**3),
        'file_count': file_count,
        'has_sss_shares': has_sss,
        'sss_file_count': sss_files
    }