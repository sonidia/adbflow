import sys, os, shutil, subprocess, time
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHBoxLayout, QMenu
from PySide6.QtCore import QTimer, QPoint
from PySide6.QtGui import QAction, QIcon
from helpers.csv import CSVHelper
from main import open_firefox, install_cookie_extension, import_cookie, setup_adb_keyboard

class CookieLoaderGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.app_name = "App"
        self.icon = "icon.png"
        self.cookies_folder = "cookies"
        self.data_csv = "data.csv"
        self.status_timer = QTimer()
        self.status_timer.setSingleShot(True)
        self.status_timer.timeout.connect(self.reset_window_title)
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.app_name)
        self.setGeometry(300, 300, 800, 600)
        app.setWindowIcon(QIcon(self.icon))

        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        self.load_button = QPushButton('Load Cookie')
        self.load_button.clicked.connect(self.load_cookies)
        button_layout.addWidget(self.load_button)

        self.refresh_button = QPushButton('Refresh data')
        self.refresh_button.clicked.connect(self.refresh_devices_and_csv)
        button_layout.addWidget(self.refresh_button)

        self.setup_keyboard_button = QPushButton('Setup Keyboard')
        self.setup_keyboard_button.clicked.connect(self.setup_keyboard_for_all)
        button_layout.addWidget(self.setup_keyboard_button)

        self.start_all_button = QPushButton('Start All')
        self.start_all_button.clicked.connect(self.start_all_flows)
        button_layout.addWidget(self.start_all_button)

        self.options_button = QPushButton('▼')
        self.options_button.setMaximumWidth(25)
        self.options_menu = QMenu(self)

        self.open_firefox_action = QAction('Open Firefox', self)
        self.open_firefox_action.setCheckable(True)
        self.open_firefox_action.setChecked(True)
        self.options_menu.addAction(self.open_firefox_action)

        self.install_cookie_action = QAction('Install Cookie Extension', self)
        self.install_cookie_action.setCheckable(True)
        self.install_cookie_action.setChecked(True)
        self.options_menu.addAction(self.install_cookie_action)

        self.import_cookie_action = QAction('Import Cookie', self)
        self.import_cookie_action.setCheckable(True)
        self.import_cookie_action.setChecked(True)
        self.options_menu.addAction(self.import_cookie_action)

        def open_menu():
            pos = self.options_button.mapToGlobal(self.options_button.rect().topLeft())
            menu_width = self.options_menu.sizeHint().width()
            self.options_menu.popup(QPoint(pos.x() - menu_width, pos.y()))

        self.options_button.clicked.connect(lambda: open_menu())
        button_layout.addWidget(self.options_button)
        layout.addLayout(button_layout)

        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Model', 'Serial', 'Username', 'Cookie File'])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
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

    def load_cookies(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Text files (*.txt)")
        file_dialog.setViewMode(QFileDialog.ViewMode.List)

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()

            if not os.path.exists(self.cookies_folder):
                os.makedirs(self.cookies_folder)

            copied_files = []
            for file_path in selected_files:
                filename = os.path.basename(file_path)
                destination = os.path.join(self.cookies_folder, filename)
                shutil.copy2(file_path, destination)
                copied_files.append(destination)

            self.update_status(f'Successfully loaded {len(copied_files)} cookie files')

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
            self.table.setColumnCount(4)

            for row_idx in range(num_rows):
                model = rows[row_idx][0] if row_idx < len(rows) and len(rows[row_idx]) > 0 else ""
                self.table.setItem(row_idx, 0, QTableWidgetItem(model))

                serial = rows[row_idx][1] if row_idx < len(rows) and len(rows[row_idx]) > 1 else ""
                self.table.setItem(row_idx, 1, QTableWidgetItem(serial))

                username = rows[row_idx][2] if row_idx < len(rows) and len(rows[row_idx]) > 2 else ""
                self.table.setItem(row_idx, 2, QTableWidgetItem(username))

                cookie_file = rows[row_idx][3] if row_idx < len(rows) and len(rows[row_idx]) > 3 else ""
                self.table.setItem(row_idx, 3, QTableWidgetItem(cookie_file))

            self.table.resizeColumnsToContents()

            self.update_status(f'Loaded {len(rows)} rows from CSV')

        except Exception as e:
            self.update_status(f'Error refreshing table: {str(e)}')
            print(f"Error details: {e}")

    def refresh_devices_and_csv(self):
        try:
            devices = self.get_devices_with_model()

            cookie_files = []
            if os.path.exists(self.cookies_folder):
                for file in os.listdir(self.cookies_folder):
                    if file.endswith('.txt'):
                        cookie_files.append(file)

            rows = []
            max_rows = max(len(devices), len(cookie_files))

            from utils.text import detect_username_from_cookie_filename
            for i in range(max_rows):
                model = devices[i]["model"] if i < len(devices) else ""
                serial = devices[i]["serial"] if i < len(devices) else ""
                cookie_file = (self.cookies_folder + "/" + cookie_files[i]) if i < len(cookie_files) else ""
                username = detect_username_from_cookie_filename(cookie_file) if cookie_file else ""
                rows.append([model, serial, username, cookie_file])

            CSVHelper.write_csv(self.data_csv, rows)

            self.refresh_table()
            self.update_status(f'Updated with {len(devices)} devices and {len(cookie_files)} cookie files')

        except Exception as e:
            self.update_status(f'Error refreshing devices: {str(e)}')
            print(f"Error details: {e}")

    def start_all_flows(self):
        try:
            row_count = self.table.rowCount()
            if row_count == 0:
                self.update_status('No devices found in table')
                return

            successful_devices = 0
            for row in range(row_count):
                serial_item = self.table.item(row, 1)
                cookie_path_item = self.table.item(row, 3)
                if not cookie_path_item or not cookie_path_item.text():
                    self.update_status(f'Row {row}: missing cookie path')
                    continue
                if serial_item and serial_item.text():
                    serial = serial_item.text()
                    try:
                        if self.open_firefox_action.isChecked():
                            open_firefox(serial)
                            time.sleep(2)

                        if self.install_cookie_action.isChecked():
                            install_cookie_extension(serial)
                            time.sleep(2)

                        if self.import_cookie_action.isChecked():
                            import_cookie(serial, cookie_path_item.text() if cookie_path_item else "")
                            time.sleep(2)

                        successful_devices += 1
                        print(f"✅ Completed flow for device: {serial}")
                    except Exception as e:
                        print(f"❌ Error processing device {serial}: {str(e)}")

            self.update_status(f'Successfully processed {successful_devices} out of {row_count} devices')

        except Exception as e:
            self.update_status(f'Error starting flows: {str(e)}')
            print(f"Error details: {e}")

    def setup_keyboard_for_all(self):
        try:
            row_count = self.table.rowCount()
            if row_count == 0:
                self.update_status('No devices found in table')
                return

            successful_devices = 0
            for row in range(row_count):
                serial_item = self.table.item(row, 1)
                if serial_item and serial_item.text():
                    serial = serial_item.text()
                    try:
                        setup_adb_keyboard(serial)
                        successful_devices += 1
                        print(f"✅ Setup keyboard for device: {serial}")
                    except Exception as e:
                        print(f"❌ Error setting up keyboard for device {serial}: {str(e)}")

            self.update_status(f'Successfully setup keyboard for {successful_devices} out of {row_count} devices')

        except Exception as e:
            self.update_status(f'Error setting up keyboard: {str(e)}')
            print(f"Error details: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = CookieLoaderGUI()
    gui.show()
    sys.exit(app.exec())