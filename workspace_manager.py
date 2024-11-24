from datetime import datetime
import os
import json
import sys
import win32gui
import win32process
import win32con
import psutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QTreeWidget, QTreeWidgetItem, QPushButton, QLabel, 
                            QSpinBox, QSystemTrayIcon, QMenu, QStyle, 
                            QScrollArea, QStyleFactory,
                            QDialog, QCheckBox, QComboBox, QLineEdit, QGroupBox, QListWidget)
from PyQt6.QtCore import QTimer, Qt, pyqtSlot
from PyQt6.QtGui import QIcon, QPalette, QColor, QFont

class WorkspaceManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Workspace Manager")
        self.setGeometry(100, 100, 1000, 700)
        
        # Initialize variables
        self.workspaces = {}
        self.save_interval = 30  # seconds
        self.workspace_dir = "saved_workspaces"
        self.current_workspace = None
        self.excluded_processes = set()
        self.show_notifications = True  # New notification control
        self.auto_save_enabled = True   # New auto-save control
        
        # Create workspace directory if it doesn't exist
        if not os.path.exists(self.workspace_dir):
            os.makedirs(self.workspace_dir)
        
        # Load settings
        self.load_settings()
        
        # Set dark theme
        self.setup_dark_theme()
        
        # Load existing workspaces
        self.load_workspaces()
        
        # Setup UI
        self.init_ui()
        
        # Setup auto-save timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.auto_save_workspace)
        if self.auto_save_enabled:
            self.timer.start(self.save_interval * 1000)
        
        # Setup system tray
        self.setup_system_tray()

    def setup_dark_theme(self):
        app = QApplication.instance()
        app.setStyle(QStyleFactory.create("Fusion"))
        
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(35, 35, 35))

        app.setPalette(dark_palette)
        
        # Set stylesheet for custom styling
        app.setStyleSheet("""
            QMainWindow {
                background-color: #353535;
            }
            QPushButton {
                background-color: #2a82da;
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3292ea;
            }
            QPushButton:pressed {
                background-color: #1a72ca;
            }
            QTreeWidget {
                background-color: #252525;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 5px;
            }
            QTreeWidget::item {
                background-color: #353535;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px;
                margin: 2px;
            }
            QTreeWidget::item:selected {
                background-color: #2a82da;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 12px;
            }
            QSpinBox {
                background-color: #252525;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 5px;
                color: white;
            }
        """)

    def init_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        
        # Create top filter bar
        filter_layout = QHBoxLayout()
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Today", "Last 7 Days", "Last 30 Days", "Custom"])
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search workspaces...")
        self.search_input.textChanged.connect(self.apply_filter)
        
        filter_layout.addWidget(QLabel("Filter:"))
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addWidget(self.search_input)
        main_layout.addLayout(filter_layout)
        
        # Split into left and right panels
        split_layout = QHBoxLayout()
        
        # Left panel (workspace list)
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Workspace Tree Widget instead of List
        self.workspace_tree = QTreeWidget()
        self.workspace_tree.setHeaderLabels(["Workspaces"])
        self.workspace_tree.setExpandsOnDoubleClick(True)
        self.workspace_tree.itemClicked.connect(self.workspace_selected)
        left_layout.addWidget(self.workspace_tree)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Add Save Current button back
        save_button = QPushButton("Save Current")
        save_button.clicked.connect(self.save_current_workspace)
        button_layout.addWidget(save_button)
        
        restore_button = QPushButton("Restore")
        restore_button.clicked.connect(self.restore_workspace)
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_workspace)
        button_layout.addWidget(restore_button)
        button_layout.addWidget(delete_button)
        left_layout.addLayout(button_layout)
        
        left_panel.setLayout(left_layout)
        
        # Right panel (settings)
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # Settings group
        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout()
        
        # Notification toggle
        self.notification_checkbox = QCheckBox("Show Notifications")
        self.notification_checkbox.setChecked(self.show_notifications)
        self.notification_checkbox.stateChanged.connect(self.toggle_notifications)
        settings_layout.addWidget(self.notification_checkbox)
        
        # Auto-save settings
        self.auto_save_checkbox = QCheckBox("Auto Save")
        self.auto_save_checkbox.setChecked(self.auto_save_enabled)
        self.auto_save_checkbox.stateChanged.connect(self.toggle_auto_save)
        settings_layout.addWidget(self.auto_save_checkbox)
        
        # Save interval
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Save Interval (seconds):"))
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(30, 3600)
        self.interval_spinbox.setValue(self.save_interval)
        self.interval_spinbox.valueChanged.connect(self.update_save_interval)
        interval_layout.addWidget(self.interval_spinbox)
        settings_layout.addLayout(interval_layout)
        
        # Process manager button
        process_manager_button = QPushButton("Process Manager")
        process_manager_button.clicked.connect(self.show_process_manager)
        settings_layout.addWidget(process_manager_button)
        
        settings_group.setLayout(settings_layout)
        right_layout.addWidget(settings_group)
        right_panel.setLayout(right_layout)
        
        # Add panels to split layout
        split_layout.addWidget(left_panel, 2)  # 2:1 ratio
        split_layout.addWidget(right_panel, 1)
        
        main_layout.addLayout(split_layout)
        
        # Set the main layout on the central widget
        central_widget.setLayout(main_layout)
        
        # Update the workspace list
        self.update_workspace_list()

    def setup_system_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip('Workspace Manager')
        
        # Set icon from system
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)
        
        # Create tray menu
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show")
        save_action = tray_menu.addAction("Quick Save")
        quit_action = tray_menu.addAction("Exit")
        
        show_action.triggered.connect(self.show)
        save_action.triggered.connect(self.save_current_workspace)
        quit_action.triggered.connect(self.quit_application)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Connect double click to show window
        self.tray_icon.activated.connect(self.tray_icon_activated)

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
            self.raise_()
            self.activateWindow()

    def quit_application(self):
        QApplication.quit()

    def get_window_info(self):
        windows = []
        def enum_windows_callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if window_text and window_text != "Workspace Manager":
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        process = psutil.Process(pid)
                        
                        # Skip excluded processes
                        if process.name() in self.excluded_processes:
                            return True
                        
                        placement = win32gui.GetWindowPlacement(hwnd)
                        rect = win32gui.GetWindowRect(hwnd)
                        
                        windows.append({
                            'title': window_text,
                            'process_name': process.name(),
                            'exe': process.exe(),
                            'placement': placement,
                            'rect': rect,
                            'pid': pid,
                            'command_line': process.cmdline(),
                            'creation_time': process.create_time(),
                            'status': process.status(),
                            'window_state': 'Maximized' if placement[1] == win32con.SW_SHOWMAXIMIZED else 'Normal'
                        })
                    except (psutil.NoSuchProcess, psutil.AccessDenied, Exception) as e:
                        print(f"Error processing window {window_text}: {str(e)}")
            return True
        
        win32gui.EnumWindows(enum_windows_callback, None)
        return windows

    def save_current_workspace(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        workspace_name = f"Workspace_{timestamp}"
        
        windows = self.get_window_info()
        workspace_data = {
            'timestamp': timestamp,
            'windows': windows,
            'save_time': datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"),
            'window_count': len(windows)
        }
        
        filepath = os.path.join(self.workspace_dir, f"{workspace_name}.json")
        with open(filepath, 'w') as f:
            json.dump(workspace_data, f, indent=4)
        
        self.workspaces[workspace_name] = workspace_data
        self.update_workspace_list()
        
        # Show notification
        if self.show_notifications:
            self.tray_icon.showMessage(
                "Workspace Saved",
                f"Saved {len(windows)} windows to {workspace_name}",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        
        return workspace_name

    def show_process_manager(self):
        dialog = ProcessManagerDialog(self.excluded_processes, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.excluded_processes = dialog.get_excluded_processes()
            self.update_exclude_list()

    def update_exclude_list(self):
        self.exclude_list.clear()
        for process in sorted(self.excluded_processes):
            self.exclude_list.addItem(process)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Workspace Manager",
            "Application minimized to system tray",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )

    def auto_save_workspace(self):
        self.save_current_workspace()

    def restore_workspace(self):
        if not self.workspace_tree.currentItem():
            return
            
        workspace_name = self.workspace_tree.currentItem().data(0, Qt.ItemDataRole.UserRole)
        workspace_data = self.workspaces.get(workspace_name)
        
        if not workspace_data:
            return
        
        # Show restoration progress
        if self.show_notifications:
            self.tray_icon.showMessage(
                "Restoring Workspace",
                f"Restoring {len(workspace_data['windows'])} windows...",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
            
        for window in workspace_data['windows']:
            try:
                # Start process if it's not running
                process_name = window['process_name']
                if not any(p.name() == process_name for p in psutil.process_iter(['name'])):
                    try:
                        os.startfile(window['exe'])
                        print(f"Starting process: {process_name}")
                        time.sleep(2)  # Give more time for the application to start
                    except Exception as e:
                        print(f"Error starting process {process_name}: {str(e)}")
                        continue
                
                # Try multiple times to find and restore the window
                max_attempts = 5
                for attempt in range(max_attempts):
                    found = False
                    
                    def find_window_callback(hwnd, _):
                        if win32gui.IsWindowVisible(hwnd):
                            if win32gui.GetWindowText(hwnd) == window['title']:
                                try:
                                    # Restore window placement
                                    win32gui.SetWindowPlacement(hwnd, window['placement'])
                                    print(f"Restored window: {window['title']}")
                                    return False  # Stop enumeration
                                except Exception as e:
                                    print(f"Error setting window placement: {str(e)}")
                        return True
                    
                    win32gui.EnumWindows(find_window_callback, None)
                    
                    if found:
                        break
                    
                    time.sleep(1)  # Wait before next attempt
                
            except Exception as e:
                print(f"Error restoring window {window['title']}: {str(e)}")
        
        # Show completion notification
        if self.show_notifications:
            self.tray_icon.showMessage(
                "Workspace Restored",
                f"Finished restoring workspace: {workspace_name}",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )

    def delete_workspace(self):
        if not self.workspace_tree.currentItem():
            return
            
        workspace_name = self.workspace_tree.currentItem().data(0, Qt.ItemDataRole.UserRole)
        filepath = os.path.join(self.workspace_dir, f"{workspace_name}.json")
        
        try:
            os.remove(filepath)
            del self.workspaces[workspace_name]
            self.update_workspace_list()
            
            # Show notification
            if self.show_notifications:
                self.tray_icon.showMessage(
                    "Workspace Deleted",
                    f"Deleted workspace: {workspace_name}",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
        except Exception as e:
            print(f"Error deleting workspace: {str(e)}")
            if self.show_notifications:
                self.tray_icon.showMessage(
                    "Error",
                    f"Failed to delete workspace: {workspace_name}",
                    QSystemTrayIcon.MessageIcon.Critical,
                    2000
                )

    def load_workspaces(self):
        if not os.path.exists(self.workspace_dir):
            return
            
        for filename in os.listdir(self.workspace_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.workspace_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        workspace_data = json.load(f)
                        workspace_name = filename[:-5]  # Remove .json
                        self.workspaces[workspace_name] = workspace_data
                except Exception as e:
                    print(f"Error loading workspace {filename}: {str(e)}")

    def update_workspace_list(self):
        self.workspace_tree.clear()
        
        for workspace_name, workspace_data in self.workspaces.items():
            try:
                # Create top-level item
                item = QTreeWidgetItem(self.workspace_tree)
                save_time = workspace_data.get('save_time', 
                    datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"))
                item.setText(0, save_time)
                item.setData(0, Qt.ItemDataRole.UserRole, workspace_name)
                
                # Add child items with details
                window_count = QTreeWidgetItem(item)
                windows = workspace_data.get('windows', [])
                window_count.setText(0, f"Windows: {len(windows)}")
                
                timestamp = QTreeWidgetItem(item)
                timestamp.setText(0, f"Created: {save_time}")
                
                # Add window details
                if windows:
                    windows_item = QTreeWidgetItem(item)
                    windows_item.setText(0, "Windows:")
                    
                    for window in windows:
                        window_item = QTreeWidgetItem(windows_item)
                        title = window.get('title', 'Unknown Window')
                        process = window.get('process_name', 'Unknown Process')
                        window_item.setText(0, f"{title} ({process})")
            except Exception as e:
                print(f"Error loading workspace {workspace_name}: {str(e)}")
                continue
        
        self.workspace_tree.sortItems(0, Qt.SortOrder.DescendingOrder)

    def apply_filter(self):
        filter_text = self.search_input.text().lower()
        filter_option = self.filter_combo.currentText()
        
        for i in range(self.workspace_tree.topLevelItemCount()):
            item = self.workspace_tree.topLevelItem(i)
            workspace_name = item.data(0, Qt.ItemDataRole.UserRole)
            workspace_data = self.workspaces[workspace_name]
            
            # Check if workspace matches filter criteria
            show_item = True
            
            # Text filter
            if filter_text:
                # Check workspace name
                if workspace_name and filter_text in workspace_name.lower():
                    show_item = True
                # Check window titles
                elif 'windows' in workspace_data:
                    show_item = any(
                        filter_text in window.get('title', '').lower() 
                        for window in workspace_data['windows']
                    )
                else:
                    show_item = False
            
            # Date filter
            if show_item and filter_option != "All":
                try:
                    # Get save_time with fallback to timestamp or current time
                    save_time_str = workspace_data.get('save_time')
                    if not save_time_str:
                        timestamp = workspace_data.get('timestamp')
                        if timestamp:
                            # Convert timestamp format to save_time format
                            temp_dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
                            save_time_str = temp_dt.strftime("%Y-%m-%d %I:%M:%S %p")
                        else:
                            # Use current time as fallback
                            save_time_str = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
                    
                    save_time = datetime.strptime(save_time_str, "%Y-%m-%d %I:%M:%S %p")
                    now = datetime.now()
                    
                    if filter_option == "Today":
                        show_item = save_time.date() == now.date()
                    elif filter_option == "Last 7 Days":
                        show_item = (now - save_time).days <= 7
                    elif filter_option == "Last 30 Days":
                        show_item = (now - save_time).days <= 30
                    elif filter_option == "Custom":
                        # You can implement custom date range dialog here
                        pass
                except Exception as e:
                    print(f"Error filtering workspace {workspace_name}: {str(e)}")
                    show_item = False
            
            item.setHidden(not show_item)

    def update_save_interval(self, value):
        """Update the auto-save interval and restart the timer"""
        self.save_interval = value
        if self.auto_save_enabled:
            self.timer.setInterval(value * 1000)  # Convert seconds to milliseconds
        self.save_settings()

    def workspace_selected(self, item):
        # Get the top-level item if a child was selected
        while item.parent():
            item = item.parent()
        
        workspace_name = item.data(0, Qt.ItemDataRole.UserRole)
        if workspace_name:
            self.current_workspace = workspace_name

    def toggle_notifications(self, state):
        self.show_notifications = bool(state)
        self.save_settings()

    def toggle_auto_save(self, state):
        self.auto_save_enabled = bool(state)
        if self.auto_save_enabled:
            self.timer.start(self.save_interval * 1000)
        else:
            self.timer.stop()
        self.save_settings()

    def show_notification(self, title, message, icon=QSystemTrayIcon.MessageIcon.Information, duration=2000):
        if self.show_notifications:
            self.tray_icon.showMessage(title, message, icon, duration)

    def save_settings(self):
        settings = {
            'show_notifications': self.show_notifications,
            'auto_save_enabled': self.auto_save_enabled,
            'save_interval': self.save_interval,
            'excluded_processes': list(self.excluded_processes)
        }
        
        settings_file = os.path.join(self.workspace_dir, 'settings.json')
        with open(settings_file, 'w') as f:
            json.dump(settings, f)

    def load_settings(self):
        settings_file = os.path.join(self.workspace_dir, 'settings.json')
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                self.show_notifications = settings.get('show_notifications', True)
                self.auto_save_enabled = settings.get('auto_save_enabled', True)
                self.save_interval = settings.get('save_interval', 30)
                self.excluded_processes = set(settings.get('excluded_processes', []))
            except Exception as e:
                print(f"Error loading settings: {str(e)}")

class ProcessManagerDialog(QDialog):
    def __init__(self, excluded_processes, parent=None):
        super().__init__(parent)
        self.excluded_processes = excluded_processes.copy()
        self.setWindowTitle("Process Manager")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Process selection
        self.process_combo = QComboBox()
        self.update_process_list()
        layout.addWidget(QLabel("Select Process:"))
        layout.addWidget(self.process_combo)
        
        # Add button
        add_button = QPushButton("Add to Excluded")
        add_button.clicked.connect(self.add_process)
        layout.addWidget(add_button)
        
        # Excluded processes list
        layout.addWidget(QLabel("Excluded Processes:"))
        self.excluded_list = QListWidget()
        self.update_excluded_list()
        layout.addWidget(self.excluded_list)
        
        # Remove button
        remove_button = QPushButton("Remove Selected")
        remove_button.clicked.connect(self.remove_process)
        layout.addWidget(remove_button)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def update_process_list(self):
        self.process_combo.clear()
        processes = set()
        for proc in psutil.process_iter(['name']):
            try:
                processes.add(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        self.process_combo.addItems(sorted(processes))

    def update_excluded_list(self):
        self.excluded_list.clear()
        self.excluded_list.addItems(sorted(self.excluded_processes))

    def add_process(self):
        process = self.process_combo.currentText()
        if process and process not in self.excluded_processes:
            self.excluded_processes.add(process)
            self.update_excluded_list()

    def remove_process(self):
        current_item = self.excluded_list.currentItem()
        if current_item:
            self.excluded_processes.remove(current_item.text())
            self.update_excluded_list()

    def get_excluded_processes(self):
        return self.excluded_processes

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WorkspaceManager()
    window.show()
    sys.exit(app.exec())