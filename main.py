import subprocess, time

def run_adb(serial, args, input_text=None, check=False):
    cmd = ["adb", "-s", serial] + args
    return subprocess.run(cmd, input=input_text, text=True, check=check, capture_output=True)

def tap(serial, x, y):
    run_adb(serial, ["shell", "input", "tap", str(x), str(y)])

def adb(serial, *args, check=True):
    return subprocess.run(
        ["adb", "-s", serial, *args],
        check=check,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def setup_adb_keyboard(
    serial: str,
    apk_path: str = "keyboard.apk",
    ime: str = "com.android.adbkeyboard/.AdbIME"
):
    adb(serial, "install", "-r", apk_path)
    adb(serial, "shell", "ime", "enable", ime)
    adb(serial, "shell", "ime", "set", ime)

def open_firefox(serial):
    run_adb(serial, [
        "shell", "monkey",
        "-p", "org.mozilla.firefox",
        "-c", "android.intent.category.LAUNCHER",
        "1"
    ])

def open_url_in_firefox(serial, url):
    run_adb(serial, [
        "shell", "am", "start",
        "-a", "android.intent.action.VIEW",
        "-d", url
    ])

def install_cookie_extension(serial):
    open_url_in_firefox(serial, "https://addons.mozilla.org/firefox/addon/cookie-editor")
    time.sleep(3)
    tap(serial, 523, 1794)
    time.sleep(2)
    tap(serial, 871, 1958)
    time.sleep(2)
    tap(serial, 901, 1963)

def import_cookie(serial, cookie_path):
    open_url_in_firefox(serial, "https://tiktok.com/profile")
    time.sleep(2)
    tap(serial, 1007, 157)
    tap(serial, 523, 1071)
    tap(serial, 565, 359)
    time.sleep(1)
    tap(serial, 406, 1984)
    time.sleep(1)
    tap(serial, 680, 1981)
    time.sleep(1)

    from helpers.file import read_file
    cookie_data = read_file(cookie_path)
    time.sleep(0.5)

    from utils.text import extract_tiktok_cookies, to_base64
    filtered = extract_tiktok_cookies(cookie_data)
    time.sleep(0.5)
    b64_filtered = to_base64(filtered)
    tap(serial, 83, 842)
    time.sleep(0.5)

    subprocess.run(["adb", "-s", serial, "shell", "am", "broadcast", "-a", "ADB_INPUT_B64", "--es", "msg", b64_filtered])
    time.sleep(1)

    tap(serial, 817, 1920)
    time.sleep(1)

    open_url_in_firefox(serial, "https://tiktok.com/profile")