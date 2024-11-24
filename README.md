# Workspace Manager

A powerful Python-based workspace management tool that helps you save, restore, and manage your window configurations across sessions.

## Table of Contents
- [Workspace Manager](#workspace-manager)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Features](#features)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Getting Started](#getting-started)
    - [Main Interface](#main-interface)
    - [Saving Workspaces](#saving-workspaces)
    - [Restoring Workspaces](#restoring-workspaces)
    - [Managing Workspaces](#managing-workspaces)
    - [Filtering and Search](#filtering-and-search)
    - [System Tray Integration](#system-tray-integration)
    - [Process Management](#process-management)
  - [Configuration](#configuration)
  - [Troubleshooting](#troubleshooting)
  - [Contributing](#contributing)

## Overview

Workspace Manager is a desktop application that automatically tracks and restores your window configurations. It helps you maintain consistent workspace setups across different sessions, making it perfect for users who work with multiple applications and window arrangements.

## Features

- **Window State Tracking**
  - Captures window positions, sizes, and states
  - Tracks associated processes and commands
  - Supports maximized and normal window states

- **Workspace Management**
  - Save current window configuration manually or automatically
  - Restore workspaces with a single click
  - Delete unused workspaces
  - Filter and search through saved workspaces

- **User Interface**
  - Modern dark theme interface
  - System tray integration
  - Collapsible workspace details
  - Real-time search and filtering

- **Automation**
  - Configurable auto-save intervals
  - Process exclusion management
  - Automatic window restoration

- **Notifications**
  - System tray notifications for important events
  - Configurable notification settings

## Requirements

- Windows Operating System
- Python 3.6 or higher
- Required Python packages:
  ```
  pywin32==306
  psutil==5.9.5
  PyQt6==6.4.2
  python-dateutil==2.8.2
  ```

## Installation

1. Clone or download the repository:
   ```bash
   git clone https://github.com/themrsami/Windows-Workspace-Manager-Python-GUI
   cd workspace-manager
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python workspace_manager.py
   ```

## Usage

### Getting Started

1. Launch the application by running `workspace_manager.py`
2. The application will start minimized in the system tray
3. Click the system tray icon to show the main window
4. Configure your preferences in the Settings panel

### Main Interface

The interface is divided into three main sections:
1. **Filter Bar** (Top)
   - Search box for finding workspaces
   - Date filter dropdown

2. **Workspace List** (Left)
   - List of saved workspaces
   - Collapsible details for each workspace
   - Action buttons (Save, Restore, Delete)

3. **Settings Panel** (Right)
   - Notification toggle
   - Auto-save configuration
   - Process management

### Saving Workspaces

- **Manual Save**
  1. Click "Save Current" to capture current window configuration
  2. The workspace will be saved with timestamp as name
  3. A notification will confirm the save

- **Auto Save**
  1. Enable "Auto Save" in settings
  2. Set desired save interval (30-3600 seconds)
  3. Workspaces will be automatically saved at the specified interval

### Restoring Workspaces

1. Select a workspace from the list
2. Click "Restore" to restore the window configuration
3. The application will:
   - Start any closed applications
   - Position windows according to saved configuration
   - Restore window states (maximized/normal)

### Managing Workspaces

- **View Details**
  - Click on a workspace to expand/collapse details
  - View window count, timestamp, and window list

- **Delete Workspace**
  1. Select the workspace to delete
  2. Click "Delete" button
  3. Confirm deletion when prompted

### Filtering and Search

- **Text Search**
  - Type in the search box to filter by:
    - Workspace names
    - Window titles
    - Process names

- **Date Filters**
  - "All": Show all workspaces
  - "Today": Today's workspaces
  - "Last 7 Days": Week's workspaces
  - "Last 30 Days": Month's workspaces
  - "Custom": Custom date range

### System Tray Integration

- Right-click the system tray icon for quick actions:
  - Show/Hide main window
  - Save current workspace
  - Exit application

### Process Management

1. Click "Process Manager" in settings
2. View list of running processes
3. Select processes to exclude from workspace management
4. Excluded processes won't be tracked or restored

## Configuration

Settings are automatically saved and include:
- Show/Hide notifications
- Auto-save enable/disable
- Save interval
- Excluded processes

Settings are stored in:
```
[user_directory]/saved_workspaces/settings.json
```

## Troubleshooting

Common issues and solutions:

1. **Windows Not Restoring**
   - Check if the application is still running
   - Verify process isn't excluded
   - Try running with administrator privileges

2. **Auto-save Not Working**
   - Verify auto-save is enabled
   - Check save interval setting
   - Ensure write permissions in save directory

3. **Missing Windows**
   - Some applications may not support window management
   - Check process exclusion list
   - Verify application is still installed

## Contributing

Contributions are welcome! Please feel free to submit pull requests or create issues for bugs and feature requests.
