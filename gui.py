import sys, os, subprocess
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTableWidget, QTableWidgetItem, QHBoxLayout
from PySide6.QtCore import QTimer, QThread, Signal
from PySide6.QtGui import QIcon
from helpers.csv import CSVHelper
from main import setup_adb_keyboard, install_chrome

class Worker(QThread):
    progress = Signal(str)
    finished = Signal(str)

    def __init__(self, task_type, table_data=None, settings=None):
        super().__init__()
        self.task_type = task_type
        self.table_data = table_data
        self.settings = settings or {}

    def run(self):
        try:
            if self.task_type == "setup_keyboard":
                self.setup_keyboard_for_all()
            elif self.task_type == "install_chrome":
                self.install_chrome_for_all()
        except Exception as e:
            self.finished.emit(f'Error: {str(e)}')

    def setup_keyboard_for_all(self):
        row_count = len(self.table_data)
        if row_count == 0:
            self.finished.emit('No devices found in table')
            return

        successful_devices = 0
        for row in range(row_count):
            serial = self.table_data[row].get('serial', '')

            if serial:
                try:
                    self.progress.emit(f'Setting up keyboard for: {serial}')
                    setup_adb_keyboard(serial)
                    successful_devices += 1
                    self.progress.emit(f'✅ Setup keyboard for device: {serial}')
                except Exception as e:
                    self.progress.emit(f'❌ Error setting up keyboard for device {serial}: {str(e)}')

        self.finished.emit(f'Successfully setup keyboard for {successful_devices} out of {row_count} devices')

    def install_chrome_for_all(self):
        row_count = len(self.table_data)
        if row_count == 0:
            self.finished.emit('No devices found in table')
            return

        successful_devices = 0
        for row in range(row_count):
            serial = self.table_data[row].get('serial', '')

            if serial:
                try:
                    self.progress.emit(f'Installing Chrome for: {serial}')
                    install_chrome(serial)
                    successful_devices += 1
                    self.progress.emit(f'✅ Installed Chrome for device: {serial}')
                except Exception as e:
                    self.progress.emit(f'❌ Error installing Chrome for device {serial}: {str(e)}')

        self.finished.emit(f'Successfully installed Chrome for {successful_devices} out of {row_count} devices')

class CookieLoaderGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.app_name = "Adbflow"
        self.icon = "icon.png"
        self.data_csv = "data.csv"
        self.status_timer = QTimer()
        self.status_timer.setSingleShot(True)
        self.status_timer.timeout.connect(self.reset_window_title)

        self.worker = None

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.app_name)
        self.setGeometry(300, 300, 800, 600)
        self.setWindowIcon(QIcon(self.icon))

        layout = QHBoxLayout()

        # Left navigation panel
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        left_panel.setMaximumWidth(160)  # Set maximum width for navigation panel

        self.refresh_button = QPushButton('Refresh data')
        self.refresh_button.clicked.connect(self.refresh_devices_and_csv)
        left_layout.addWidget(self.refresh_button)

        self.setup_keyboard_button = QPushButton('Setup Keyboard')
        self.setup_keyboard_button.clicked.connect(self.setup_keyboard_for_all)
        left_layout.addWidget(self.setup_keyboard_button)

        self.install_chrome_button = QPushButton('Install Chrome')
        self.install_chrome_button.clicked.connect(self.install_chrome_for_all)
        left_layout.addWidget(self.install_chrome_button)

        # Add stretch to push buttons to top
        left_layout.addStretch()

        # Right content panel
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)

        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['Model', 'Serial'])
        self.table.horizontalHeader().setStretchLastSection(True)
        right_layout.addWidget(self.table)

        layout.addWidget(left_panel)
        layout.addWidget(right_panel)
        self.setLayout(layout)
        self.refresh_table()

    def update_status(self, text):
        if text:
            self.setWindowTitle(f'{self.app_name} - {text}')
            self.status_timer.start(5000)
        else:
            self.reset_window_title()

    def reset_window_title(self):
        self.setWindowTitle(self.app_name)

    def get_devices_with_model(self):
        try:
            out = subprocess.check_output(["adb", "devices", "-l"], text=True)
            lines = out.strip().splitlines()[1:]

            devices = []
            for line in lines:
                if "device" not in line:
                    continue

                parts = line.split()
                serial = parts[0]

                model = "UNKNOWN"
                for p in parts:
                    if p.startswith("model:"):
                        model = p.split("model:")[1]
                        break

                devices.append({
                    "serial": serial,
                    "model": model,
                    "raw": line
                })

            return devices
        except Exception as e:
            print(f"Error getting devices: {e}")
            return []

    def refresh_table(self):
        try:
            try:
                rows = CSVHelper.read_csv(self.data_csv)
            except FileNotFoundError:
                rows = []

            num_rows = len(rows)
            if num_rows == 0:
                self.table.setRowCount(0)
                self.update_status('No data in CSV found')
                return

            self.table.setRowCount(num_rows)
            self.table.setColumnCount(2)

            for row_idx in range(num_rows):
                model = rows[row_idx][0] if row_idx < len(rows) and len(rows[row_idx]) > 0 else ""
                self.table.setItem(row_idx, 0, QTableWidgetItem(model))

                serial = rows[row_idx][1] if row_idx < len(rows) and len(rows[row_idx]) > 1 else ""
                self.table.setItem(row_idx, 1, QTableWidgetItem(serial))

            self.table.resizeColumnsToContents()

            self.update_status(f'Loaded {len(rows)} rows from CSV')

        except Exception as e:
            self.update_status(f'Error refreshing table: {str(e)}')
            print(f"Error details: {e}")

    def refresh_devices_and_csv(self):
        try:
            devices = self.get_devices_with_model()

            rows = []
            for i in range(len(devices)):
                model = devices[i]["model"]
                serial = devices[i]["serial"]
                rows.append([model, serial])

            CSVHelper.write_csv(self.data_csv, rows)

            self.refresh_table()
            self.update_status(f'Updated with {len(devices)} devices')

        except Exception as e:
            self.update_status(f'Error refreshing devices: {str(e)}')
            print(f"Error details: {e}")

    def on_worker_finished(self, message):
        self.update_status(message)
        self.enable_buttons()
        self.worker = None

    def disable_buttons(self):
        self.refresh_button.setEnabled(False)
        self.setup_keyboard_button.setEnabled(False)
        self.install_chrome_button.setEnabled(False)

    def enable_buttons(self):
        self.refresh_button.setEnabled(True)
        self.setup_keyboard_button.setEnabled(True)
        self.install_chrome_button.setEnabled(True)

    def install_chrome_for_all(self):
        if self.worker and self.worker.isRunning():
            self.update_status('Task already running')
            return

        table_data = []
        row_count = self.table.rowCount()
        for row in range(row_count):
            serial_item = self.table.item(row, 1)
            serial = serial_item.text() if serial_item else ""
            table_data.append({'serial': serial})

        self.disable_buttons()

        self.worker = Worker("install_chrome", table_data)
        self.worker.progress.connect(self.update_status)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()

    def setup_keyboard_for_all(self):
        if self.worker and self.worker.isRunning():
            self.update_status('Task already running')
            return

        table_data = []
        row_count = self.table.rowCount()
        for row in range(row_count):
            serial_item = self.table.item(row, 1)
            serial = serial_item.text() if serial_item else ""
            table_data.append({
                'serial': serial
            })

        self.disable_buttons()

        self.worker = Worker("setup_keyboard", table_data)
        self.worker.progress.connect(self.update_status)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = CookieLoaderGUI()
    gui.show()
    sys.exit(app.exec())