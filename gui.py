import sys, os, subprocess
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTableWidget, QTableWidgetItem, QHBoxLayout
from PySide6.QtCore import QTimer, QThread, Signal, Qt
from PySide6.QtGui import QIcon
from helpers.csv import CSVHelper
from main import setup_adb_keyboard, install_chrome, open_url_in_chrome, run_ads_automation

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
            elif self.task_type == "open_ads":
                self.open_ads_for_all()
            elif self.task_type == "run_ads":
                self.run_ads_for_all()
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

    def open_ads_for_all(self):
        row_count = len(self.table_data)
        if row_count == 0:
            self.finished.emit('No devices found in table')
            return

        successful_devices = 0
        for row in self.table_data:
            serial = row.get('serial', '')
            ads_link = row.get('ads_link', '')

            if not serial:
                continue
            if not ads_link:
                self.progress.emit(f'⚠️ No ads link for device: {serial}')
                continue

            try:
                self.progress.emit(f'Opening ads for: {serial}')
                open_url_in_chrome(serial, ads_link)
                successful_devices += 1
                self.progress.emit(f'✅ Opened ads on device: {serial}')
            except Exception as e:
                self.progress.emit(f'❌ Error on device {serial}: {str(e)}')

        self.finished.emit(f'Successfully opened ads on {successful_devices} out of {row_count} devices')

    def run_ads_for_all(self):
        row_count = len(self.table_data)
        if row_count == 0:
            self.finished.emit('No devices found in table')
            return

        successful_devices = 0
        for row in self.table_data:
            serial = row.get('serial', '')
            ads_link = row.get('ads_link', '')

            if not serial:
                continue
            if not ads_link:
                self.progress.emit(f'⚠️ No ads link for device: {serial}')
                continue

            try:
                self.progress.emit(f'🤖 Running ads automation on: {serial}')
                title = run_ads_automation(serial, ads_link)
                successful_devices += 1
                self.progress.emit(f'✅ Done on {serial} — page: {title}')
            except Exception as e:
                self.progress.emit(f'❌ Error on device {serial}: {str(e)}')

        self.finished.emit(f'Ads automation done: {successful_devices}/{row_count} devices')

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

        self.open_ads_button = QPushButton('Open Ads')
        self.open_ads_button.clicked.connect(self.open_ads_for_all)
        left_layout.addWidget(self.open_ads_button)

        self.run_ads_button = QPushButton('Run Ads')
        self.run_ads_button.clicked.connect(self.run_ads_for_all)
        left_layout.addWidget(self.run_ads_button)

        # Add stretch to push buttons to top
        left_layout.addStretch()

        # Right content panel
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)

        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Model', 'Serial', 'Ads Link'])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.itemChanged.connect(self.on_table_item_changed)
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

            self.table.blockSignals(True)
            self.table.setRowCount(num_rows)
            self.table.setColumnCount(3)

            for row_idx in range(num_rows):
                model = rows[row_idx][0] if len(rows[row_idx]) > 0 else ""
                serial = rows[row_idx][1] if len(rows[row_idx]) > 1 else ""
                ads_link = rows[row_idx][2] if len(rows[row_idx]) > 2 else ""

                model_item = QTableWidgetItem(model)
                serial_item = QTableWidgetItem(serial)
                ads_item = QTableWidgetItem(ads_link)

                # Model và Serial không cho edit trực tiếp
                non_editable = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
                model_item.setFlags(non_editable)
                serial_item.setFlags(non_editable)

                self.table.setItem(row_idx, 0, model_item)
                self.table.setItem(row_idx, 1, serial_item)
                self.table.setItem(row_idx, 2, ads_item)

            self.table.resizeColumnsToContents()
            self.table.blockSignals(False)

            self.update_status(f'Loaded {len(rows)} rows from CSV')

        except Exception as e:
            self.update_status(f'Error refreshing table: {str(e)}')
            print(f"Error details: {e}")

    def refresh_devices_and_csv(self):
        try:
            devices = self.get_devices_with_model()

            # Đọc ads_link cũ từ CSV (nếu có) để giữ lại khi refresh
            try:
                existing = CSVHelper.read_csv(self.data_csv)
                existing_links = {row[1]: row[2] for row in existing if len(row) > 2}
            except Exception:
                existing_links = {}

            rows = []
            for device in devices:
                serial = device["serial"]
                ads_link = existing_links.get(serial, "")
                rows.append([device["model"], serial, ads_link])

            CSVHelper.write_csv(self.data_csv, rows)

            self.refresh_table()
            self.update_status(f'Updated with {len(devices)} devices')

        except Exception as e:
            self.update_status(f'Error refreshing devices: {str(e)}')
            print(f"Error details: {e}")

    def on_table_item_changed(self, item):
        """Lưu CSV mỗi khi user chỉnh sửa ô Ads Link."""
        if item.column() != 2:
            return
        try:
            rows = []
            for row_idx in range(self.table.rowCount()):
                model = self.table.item(row_idx, 0)
                serial = self.table.item(row_idx, 1)
                ads = self.table.item(row_idx, 2)
                rows.append([
                    model.text() if model else "",
                    serial.text() if serial else "",
                    ads.text() if ads else "",
                ])
            CSVHelper.write_csv(self.data_csv, rows)
        except Exception as e:
            print(f"Error saving ads link: {e}")

    def on_worker_finished(self, message):
        self.update_status(message)
        self.enable_buttons()
        self.worker = None

    def disable_buttons(self):
        self.refresh_button.setEnabled(False)
        self.setup_keyboard_button.setEnabled(False)
        self.install_chrome_button.setEnabled(False)
        self.open_ads_button.setEnabled(False)
        self.run_ads_button.setEnabled(False)

    def enable_buttons(self):
        self.refresh_button.setEnabled(True)
        self.setup_keyboard_button.setEnabled(True)
        self.install_chrome_button.setEnabled(True)
        self.open_ads_button.setEnabled(True)
        self.run_ads_button.setEnabled(True)

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

    def open_ads_for_all(self):
        if self.worker and self.worker.isRunning():
            self.update_status('Task already running')
            return

        table_data = []
        row_count = self.table.rowCount()
        for row in range(row_count):
            serial_item = self.table.item(row, 1)
            ads_item = self.table.item(row, 2)
            serial = serial_item.text() if serial_item else ""
            ads_link = ads_item.text() if ads_item else ""
            table_data.append({'serial': serial, 'ads_link': ads_link})

        self.disable_buttons()

        self.worker = Worker("open_ads", table_data)
        self.worker.progress.connect(self.update_status)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()

    def run_ads_for_all(self):
        if self.worker and self.worker.isRunning():
            self.update_status('Task already running')
            return

        table_data = []
        row_count = self.table.rowCount()
        for row in range(row_count):
            serial_item = self.table.item(row, 1)
            ads_item = self.table.item(row, 2)
            serial = serial_item.text() if serial_item else ""
            ads_link = ads_item.text() if ads_item else ""
            table_data.append({'serial': serial, 'ads_link': ads_link})

        self.disable_buttons()

        self.worker = Worker("run_ads", table_data)
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