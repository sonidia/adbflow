# Adbflow

A comprehensive GUI tool for mobile automation that manages cookie files and performs automated TikTok cookie importing on Android devices using ADB.

## Features

- **GUI Interface**: PySide6-based desktop application for easy cookie management
- **Automated Cookie Import**: Automated workflow to import TikTok cookies into Firefox on mobile devices
- **Device Management**: Automatic detection and management of connected Android devices
- **CSV Data Management**: Built-in CSV helper utilities for data manipulation
- **ADB Integration**: Full ADB command integration for device control
- **Build Tools**: PyInstaller build scripts for creating executables
- **Installer**: Automated setup script for ADB and scrcpy tools

## Project Structure

### Core Files

- **`main.py`** - Main automation logic for ADB operations and cookie importing
- **`gui.py`** - PySide6 GUI application for cookie management and device control
- **`data.csv`** - CSV file containing device serials and cookie file mappings

### Helper Modules

- **`helpers/csv.py`** - CSV file manipulation utilities
- **`helpers/file.py`** - File reading and processing utilities
- **`utils/text.py`** - Text processing utilities for cookie extraction

### Build & Installation

- **`build.bat`** - Windows batch script to build executable using PyInstaller
- **`installer.bat`** - Automated installer for ADB and scrcpy tools
- **`build.spec`** - PyInstaller specification file
- **`requirements.txt`** - Python dependencies

## Installation

### Prerequisites

- Python 3.8+
- Android device with USB debugging enabled
- ADB (Android Debug Bridge) - automatically installed via `installer.bat`

### Setup Steps

1. **Clone the repository:**

   ```bash
   git clone https://github.com/sonic-media/auto-mobile.git
   cd auto-mobile
   ```

2. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Install ADB and scrcpy (Windows):**

   ```bash
   installer.bat
   ```

   This will download and install ADB and scrcpy to `C:\android-tools\`

4. **Restart your command prompt** to refresh the PATH environment variable.

## Usage

### GUI Application

1. **Launch the GUI:**

   ```bash
   python gui.py
   ```

2. **Load Cookies:**
   - Click "Load Cookie" to select and upload `.txt` cookie files
   - Files are automatically copied to the `cookies/` directory

3. **Refresh Device Data:**
   - Click "Refresh data" to scan connected devices and update the table
   - Displays device model, serial, username, and associated cookie files

4. **Setup ADB Keyboard:**
   - Click "Setup Keyboard" to install ADB keyboard on all connected devices
   - Required for automated text input

5. **Start Automation:**
   - Click "Start All" to begin the automated cookie import process for all devices

### Manual ADB Setup

Before using the automation, ensure your device is properly connected:

```bash
# Enable TCP/IP mode on device
adb tcpip 5555

# Connect via WiFi (replace with your device IP)
adb connect 192.168.1.100:5555
```

## Building Executable

To create a standalone executable:

```bash
build.bat
```

This will generate:

- `dist/gui.exe` - Main GUI executable
- `dist/main.exe` - Command-line automation tool

## Automation Flow

The automation performs the following steps for each device:

1. **Firefox Setup**: Opens Firefox and installs the Cookie Editor extension
2. **Cookie Import**: Navigates to TikTok profile page and imports cookies
3. **Text Input**: Uses ADB keyboard for automated text entry
4. **Verification**: Opens profile page to verify successful import

## Requirements

- Python 3.8 or higher
- PySide6 >= 6.0.0
- PyInstaller >= 6.0.0 (for building)
- Android device with Firefox installed
- USB debugging enabled on device
- ADB (automatically installed via installer)

## Troubleshooting

### Common Issues

1. **ADB not found**: Run `installer.bat` and restart your command prompt
2. **Device not detected**: Ensure USB debugging is enabled and device is authorized
3. **Firefox not opening**: Verify Firefox is installed on the device
4. **Cookie import fails**: Check cookie file format and Firefox extension installation

### Device Connection

```bash
# Check connected devices
adb devices

# Restart ADB server
adb kill-server
adb start-server
```

## Chrome Automation Setup (CDP)

The "Run Ads" feature uses Chrome DevTools Protocol (CDP) for browser automation on Android devices.

### How it works

```
Python app → ADB forward port → Chrome mobile → CDP WebSocket
```

### Prerequisites

- Chrome installed on Android device
- ADB (already included)

### Setup Steps

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Enable Chrome remote debugging:**

   The app automatically:
   - Starts Chrome with remote debugging
   - Forwards ADB port 9222
   - Connects via WebSocket

### Usage

1. Add ads URLs to the "Ads Link" column in the GUI
2. Click "Run Ads" button
3. CDP will automate Chrome on each device

### Customization

Edit the `run_ads_automation` function in `main.py` to add your specific automation logic:

```python
# Current implementation: Click element with text "Learn more"
js_click = """
const elements = Array.from(document.querySelectorAll('*')).filter(el =>
    el.textContent && el.textContent.trim().toLowerCase().includes('learn more')
);
if (elements.length > 0) {
    elements[0].click();
    'clicked';
} else {
    'not_found';
}
"""
result = cdp.execute_js(js_click)

# Add more actions as needed:
# cdp.click('.another-button')        # Click by CSS selector
# time.sleep(2)                       # Wait for page changes
# cdp.input_text('#input-field', 'text')  # Fill form fields
```

### Test Script

Test your ads automation with a specific URL:

```bash
python test_ads.py "https://your-ads-url-here"
```

### Available CDP methods

- `cdp.navigate(url)` - Go to URL
- `cdp.click(selector)` - Click CSS selector
- `cdp.input_text(selector, text)` - Type text into input field
- `cdp.execute_js(js)` - Run JavaScript and return result
- `cdp.get_page_title()` - Get page title

### Text-based Element Finding

For elements without reliable CSS selectors, use JavaScript to find by text content:

```python
# Find and click element containing "Learn more" (case-insensitive)
js_click = """
const elements = Array.from(document.querySelectorAll('*')).filter(el =>
    el.textContent && el.textContent.trim().toLowerCase().includes('learn more')
);
if (elements.length > 0) {
    elements[0].click();
    'clicked';
} else {
    'not_found';
}
"""
result = cdp.execute_js(js_click)
```

### Demo Script

Run the demo to see CDP in action:

```bash
python demo_cdp.py
```

### Error Handling

The automation is designed to be robust:

- If an element is not found, it logs a warning but continues
- Network timeouts are handled gracefully
- Chrome crashes are automatically recovered

Check the console output for detailed logs during automation.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
