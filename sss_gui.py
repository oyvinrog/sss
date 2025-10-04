#!/usr/bin/env python3

import sys
import os
import subprocess
import datetime
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTextEdit, QLabel, QMessageBox, QFileDialog,
    QProgressBar, QGroupBox, QListWidget, QLineEdit, QDialog,
    QListWidgetItem
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from split import split_bip39_to_shares
from combine import combine_shares_to_bip39


class USBSelectionDialog(QDialog):
    """Dialog for selecting USB drive with auto-detection."""
    
    def __init__(self, parent, share_num, initial_mounts):
        super().__init__(parent)
        self.parent_window = parent
        self.share_num = share_num
        self.initial_mounts = initial_mounts
        self.selected_path = None
        self.setWindowTitle(f"Select USB Pen #{share_num}")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.init_ui()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_usb_list)
        self.refresh_timer.start(2000)  # Refresh every 2 seconds
        
        # Initial refresh
        self.refresh_usb_list()
        
    def init_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout()
        
        # Instructions
        title = QLabel(f"📍 Please insert USB Pen #{self.share_num}")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        instruction = QLabel(
            "The list below will automatically update when you insert a USB drive.\n"
            "Select your USB drive from the list and click 'Select USB'."
        )
        instruction.setWordWrap(True)
        layout.addWidget(instruction)
        
        layout.addSpacing(10)
        
        # Status label
        self.status_label = QLabel("🔍 Scanning for USB drives...")
        layout.addWidget(self.status_label)
        
        # USB list
        self.usb_list = QListWidget()
        self.usb_list.itemDoubleClicked.connect(self.on_usb_double_clicked)
        layout.addWidget(self.usb_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("🔄 Refresh Now")
        self.refresh_button.clicked.connect(self.refresh_usb_list)
        button_layout.addWidget(self.refresh_button)
        
        button_layout.addStretch()
        
        self.select_button = QPushButton("Select USB")
        self.select_button.setEnabled(False)
        self.select_button.clicked.connect(self.on_select_clicked)
        button_layout.addWidget(self.select_button)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.on_browse_clicked)
        button_layout.addWidget(self.browse_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Connect list selection
        self.usb_list.itemSelectionChanged.connect(self.on_selection_changed)
        
    def refresh_usb_list(self):
        """Refresh the list of available USB drives."""
        current_selection = None
        if self.usb_list.currentItem():
            current_selection = self.usb_list.currentItem().data(Qt.UserRole)
        
        self.usb_list.clear()
        usb_drives = self.parent_window.detect_usb_drives()
        current_mounts = self.parent_window.get_current_mounts()
        
        # Identify newly mounted drives
        new_mounts = current_mounts - self.initial_mounts
        
        if usb_drives:
            self.status_label.setText(f"✅ Found {len(usb_drives)} USB drive(s)")
            
            for drive_path in usb_drives:
                # Get drive info
                try:
                    drive_name = os.path.basename(drive_path)
                    
                    # Get size info
                    statvfs = os.statvfs(drive_path)
                    total_size = (statvfs.f_blocks * statvfs.f_frsize) / (1024**3)  # GB
                    free_size = (statvfs.f_bavail * statvfs.f_frsize) / (1024**3)   # GB
                    
                    # Check if this is a newly mounted drive
                    is_new = drive_path in new_mounts
                    new_indicator = " 🆕 NEW" if is_new else ""
                    
                    display_text = f"{drive_name}{new_indicator}\n    Path: {drive_path}\n    Size: {total_size:.1f} GB (Free: {free_size:.1f} GB)"
                    
                    item = QListWidgetItem(display_text)
                    item.setData(Qt.UserRole, drive_path)
                    self.usb_list.addItem(item)
                    
                    # Auto-select newly mounted drives
                    if is_new or (current_selection and drive_path == current_selection):
                        self.usb_list.setCurrentItem(item)
                        
                except Exception:
                    item = QListWidgetItem(f"{os.path.basename(drive_path)}\n    Path: {drive_path}")
                    item.setData(Qt.UserRole, drive_path)
                    self.usb_list.addItem(item)
        else:
            self.status_label.setText("⏳ Waiting for USB drive... (auto-refreshing)")
    
    def on_selection_changed(self):
        """Handle selection change."""
        self.select_button.setEnabled(self.usb_list.currentItem() is not None)
    
    def on_select_clicked(self):
        """Handle select button click."""
        current_item = self.usb_list.currentItem()
        if current_item:
            self.selected_path = current_item.data(Qt.UserRole)
            self.refresh_timer.stop()
            self.accept()
    
    def on_usb_double_clicked(self, item):
        """Handle double-click on USB item."""
        self.selected_path = item.data(Qt.UserRole)
        self.refresh_timer.stop()
        self.accept()
    
    def on_browse_clicked(self):
        """Handle browse button click for manual selection."""
        usb_path = QFileDialog.getExistingDirectory(
            self,
            f"Select USB Pen #{self.share_num} Mount Point",
            "/media",
            QFileDialog.ShowDirsOnly
        )
        
        if usb_path:
            self.selected_path = usb_path
            self.refresh_timer.stop()
            self.accept()


class SSSMainWindow(QMainWindow):
    """Main window for Shamir Secret Sharing USB manager."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SSS USB Key Manager")
        self.setMinimumSize(800, 600)
        self.previous_mounts = self.get_current_mounts()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title
        title = QLabel("Shamir Secret Sharing - USB Key Manager")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Description
        desc = QLabel("Split BIP39 seed phrases into 5 shares (3-of-5 scheme) or combine shares back into seed phrase")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(desc)
        
        main_layout.addSpacing(20)
        
        # Main action buttons
        button_layout = QHBoxLayout()
        
        self.split_button = QPushButton("🔐 Split to USB Keys")
        self.split_button.setMinimumHeight(60)
        self.split_button.clicked.connect(self.start_split)
        button_layout.addWidget(self.split_button)
        
        self.combine_button = QPushButton("🔓 Combine from USB Keys")
        self.combine_button.setMinimumHeight(60)
        self.combine_button.clicked.connect(self.start_combine)
        button_layout.addWidget(self.combine_button)
        
        main_layout.addLayout(button_layout)
        
        main_layout.addSpacing(20)
        
        # Output area
        output_group = QGroupBox("Output Log")
        output_layout = QVBoxLayout()
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(300)
        output_layout.addWidget(self.output_text)
        
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
    def log(self, message):
        """Add a message to the output log."""
        self.output_text.append(message)
        self.output_text.verticalScrollBar().setValue(
            self.output_text.verticalScrollBar().maximum()
        )
    
    def get_current_mounts(self):
        """Get currently mounted filesystems."""
        mounts = set()
        try:
            with open('/proc/mounts', 'r') as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        mount_point = parts[1]
                        # Filter for likely USB mounts
                        if any(prefix in mount_point for prefix in ['/media/', '/mnt/', '/run/media/']):
                            mounts.add(mount_point)
        except Exception:
            pass
        return mounts
    
    def detect_usb_drives(self):
        """Detect available USB drives and removable media."""
        usb_drives = []
        
        # Method 1: Check common mount points
        common_paths = ['/media', '/mnt', '/run/media']
        for base_path in common_paths:
            if os.path.exists(base_path):
                try:
                    for user_dir in os.listdir(base_path):
                        user_path = os.path.join(base_path, user_dir)
                        if os.path.isdir(user_path):
                            # Check if this is a user directory or direct mount
                            if base_path == '/media' and user_dir == os.environ.get('USER', ''):
                                # Look inside user's media directory
                                for mount in os.listdir(user_path):
                                    mount_path = os.path.join(user_path, mount)
                                    if os.path.isdir(mount_path) and os.path.ismount(mount_path):
                                        usb_drives.append(mount_path)
                            elif os.path.ismount(user_path):
                                usb_drives.append(user_path)
                except Exception:
                    pass
        
        # Method 2: Parse lsblk for removable devices
        try:
            result = subprocess.run(
                ['lsblk', '-J', '-o', 'NAME,MOUNTPOINT,RM,SIZE,LABEL'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                for device in data.get('blockdevices', []):
                    if device.get('rm') == '1':  # Removable device
                        # Check device and its children for mount points
                        if device.get('mountpoint'):
                            path = device['mountpoint']
                            if path not in usb_drives:
                                usb_drives.append(path)
                        
                        for child in device.get('children', []):
                            if child.get('mountpoint'):
                                path = child['mountpoint']
                                if path not in usb_drives:
                                    usb_drives.append(path)
        except Exception:
            pass
        
        return sorted(set(usb_drives))
    
    def wait_for_new_usb(self, share_num):
        """Wait for a new USB drive to be inserted and let user select it."""
        # Use current mounts to detect new USB insertions
        initial_mounts = self.get_current_mounts()
        
        dialog = USBSelectionDialog(self, share_num, initial_mounts)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            selected_path = dialog.selected_path
            # Update previous mounts to include this selection for next iteration
            self.previous_mounts = self.get_current_mounts()
            return selected_path
        else:
            return None
        
    def start_split(self):
        """Start the split operation."""
        self.output_text.clear()
        self.log("🔐 Starting Split Operation...")
        self.log("=" * 60)
        
        # Get seed phrase from user
        seed_phrase, ok = self.get_seed_phrase_input()
        if not ok or not seed_phrase:
            self.log("❌ Operation cancelled.")
            return
        
        try:
            # Generate shares using existing function
            self.log("📝 Generating Shamir secret shares...")
            shares = split_bip39_to_shares(seed_phrase)
            self.log(f"✅ Generated {len(shares)} shares (3-of-5 scheme)")
            self.log("")
            
            # Display shares
            for i, share in enumerate(shares, 1):
                self.log(f"Share {i}: {share[:50]}...")
            self.log("")
            
            # Ask for USB pens and write shares
            self.write_shares_to_usb(shares)
            
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to split: {str(e)}")
            
    def start_combine(self):
        """Start the combine operation."""
        self.output_text.clear()
        self.log("🔓 Starting Combine Operation...")
        self.log("=" * 60)
        
        try:
            # Read shares from USB pens
            shares = self.read_shares_from_usb()
            
            if not shares:
                self.log("❌ Operation cancelled.")
                return
                
            if len(shares) < 3:
                self.log("❌ At least 3 shares are required!")
                QMessageBox.warning(self, "Insufficient Shares", "At least 3 shares are required to recover the seed phrase.")
                return
            
            # Combine shares using existing function
            self.log("")
            self.log("🔄 Combining shares...")
            recovered_phrase = combine_shares_to_bip39(shares_list=shares)
            
            self.log("")
            self.log("=" * 60)
            self.log("✅ Successfully recovered BIP39 seed phrase!")
            self.log("")
            self.log("🔑 Recovered Phrase:")
            self.log(recovered_phrase)
            self.log("=" * 60)
            
            # Show in message box too
            result_dialog = QMessageBox(self)
            result_dialog.setWindowTitle("Recovery Successful")
            result_dialog.setText("Seed phrase recovered successfully!")
            result_dialog.setDetailedText(recovered_phrase)
            result_dialog.setIcon(QMessageBox.Information)
            result_dialog.exec_()
            
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to combine: {str(e)}")
            
    def get_seed_phrase_input(self):
        """Get seed phrase input from user."""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Enter Seed Phrase")
        dialog.setMinimumWidth(600)
        
        layout = QVBoxLayout()
        
        label = QLabel("Enter your 24-word BIP39 seed phrase:")
        label.setWordWrap(True)
        layout.addWidget(label)
        
        hint_label = QLabel("Note: Words can be abbreviated to their first 4 characters")
        hint_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(hint_label)
        
        text_edit = QTextEdit()
        text_edit.setMinimumHeight(100)
        text_edit.setPlaceholderText("Enter seed phrase here (space-separated words)...")
        layout.addWidget(text_edit)
        
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            return text_edit.toPlainText().strip(), True
        else:
            return None, False
            
    def write_shares_to_usb(self, shares):
        """Write shares to USB drives sequentially."""
        self.log("💾 Ready to write shares to USB drives...")
        self.log("")
        
        for i, share in enumerate(shares, 1):
            self.log(f"📍 Preparing to write Share {i}/{len(shares)}...")
            
            # Use efficient USB selection dialog
            usb_path = self.wait_for_new_usb(i)
            
            if not usb_path:
                self.log(f"❌ Cancelled at Share {i}")
                return
            
            try:
                # Create SSS directory on USB
                sss_dir = Path(usb_path) / "SSS_Shares"
                sss_dir.mkdir(exist_ok=True)
                
                # Write share to file
                share_file = sss_dir / f"share_{i}.txt"
                with open(share_file, 'w') as f:
                    f.write(share)
                
                self.log(f"✅ Share {i} written to: {share_file}")
                
                # Write metadata file
                metadata_file = sss_dir / "README.txt"
                with open(metadata_file, 'w') as f:
                    f.write(f"SSS Share #{i} of 5\n")
                    f.write(f"Scheme: 3-of-5 (any 3 shares can recover the seed)\n")
                    f.write(f"Created by SSS USB Key Manager\n")
                    f.write(f"\n")
                    f.write(f"⚠️  KEEP THIS USB SECURE! ⚠️\n")
                
                self.log(f"📝 Metadata written to: {metadata_file}")
                self.log("")
                
            except Exception as e:
                self.log(f"❌ Error writing Share {i}: {str(e)}")
                QMessageBox.critical(self, "Write Error", f"Failed to write Share {i}: {str(e)}")
                return
        
        self.log("=" * 60)
        self.log("✅ All shares written successfully!")
        self.log("=" * 60)
        
        QMessageBox.information(
            self,
            "Success",
            f"All {len(shares)} shares have been written to USB drives successfully!\n\n"
            "Store each USB securely in a different location."
        )
        
    def read_shares_from_usb(self):
        """Read shares from USB drives."""
        self.log("📂 Ready to read shares from USB drives...")
        self.log("")
        
        shares = []
        
        # Ask how many shares to read (minimum 3, maximum 5)
        from PyQt5.QtWidgets import QInputDialog
        
        num_shares, ok = QInputDialog.getInt(
            self,
            "Number of Shares",
            "How many shares do you want to combine? (minimum 3, maximum 5)",
            3, 3, 5, 1
        )
        
        if not ok:
            return None
        
        for i in range(1, num_shares + 1):
            self.log(f"📍 Preparing to read Share {i}/{num_shares}...")
            
            # Use efficient USB selection dialog
            usb_path = self.wait_for_new_usb(i)
            
            if not usb_path:
                self.log(f"❌ Cancelled at Share {i}")
                return None
            
            try:
                # Look for SSS directory
                sss_dir = Path(usb_path) / "SSS_Shares"
                if not sss_dir.exists():
                    # Try to find any .txt file with share data
                    self.log(f"⚠️  SSS_Shares directory not found, searching for share files...")
                    share_files = list(Path(usb_path).rglob("share_*.txt"))
                    
                    if not share_files:
                        raise FileNotFoundError("No share files found on this USB")
                else:
                    # Find share file in SSS directory
                    share_files = list(sss_dir.glob("share_*.txt"))
                    
                    if not share_files:
                        raise FileNotFoundError("No share files found in SSS_Shares directory")
                
                # If multiple share files found, select the most recent one
                if len(share_files) > 1:
                    # Sort by modification time, most recent first
                    share_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                    share_file = share_files[0]
                    
                    self.log(f"ℹ️  Found {len(share_files)} share files, selecting most recent:")
                    for idx, sf in enumerate(share_files[:3], 1):  # Show top 3
                        mtime = sf.stat().st_mtime
                        mtime_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                        marker = "✓ SELECTED" if idx == 1 else ""
                        self.log(f"   {idx}. {sf.name} ({mtime_str}) {marker}")
                    if len(share_files) > 3:
                        self.log(f"   ... and {len(share_files) - 3} more")
                    self.log("")
                else:
                    share_file = share_files[0]
                
                # Read share
                with open(share_file, 'r') as f:
                    share_content = f.read().strip()
                
                shares.append(share_content)
                self.log(f"✅ Share {i} read from: {share_file}")
                self.log(f"   Preview: {share_content[:50]}...")
                self.log("")
                
            except Exception as e:
                self.log(f"❌ Error reading Share {i}: {str(e)}")
                QMessageBox.critical(self, "Read Error", f"Failed to read Share {i}: {str(e)}")
                return None
        
        self.log(f"✅ Successfully read {len(shares)} shares")
        return shares


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = SSSMainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
