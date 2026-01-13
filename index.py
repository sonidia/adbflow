import os, time

def tap(x, y):
    os.system(f"adb shell input tap {x} {y}")

def text(t):
    os.system(f'adb shell input text "{t}"')

def open_firefox():
    os.system(
        "adb shell monkey -p org.mozilla.firefox -c android.intent.category.LAUNCHER 1",
    )
import subprocess, os, time

def tap(x, y):
    os.system(f"adb shell input tap {x} {y}")

def text(t):
    os.system(f'adb shell input text "{t}"')

def get_devices():
    result = subprocess.check_output(["adb", "devices"], text=True)
    lines = result.strip().splitlines()[1:]
    devices = []
    for line in lines:
        if "\tdevice" in line:
            devices.append(line.split("\t")[0])
    return devices

def open_firefox(serial):
    model = subprocess.check_output(
        ["adb", "-s", serial, "shell", "getprop", "ro.product.model"],
        text=True
    ).strip()
    subprocess.run([
        "adb", "-s", serial,
        "shell", "monkey",
        "-p", "org.mozilla.firefox",
        "-c", "android.intent.category.LAUNCHER", "1"
    ])
    time.sleep(2)
    os.system(
        "adb shell am start -a android.intent.action.VIEW -d https://addons.mozilla.org/firefox/addon/cookie-editor org.mozilla.firefox"
    )
    time.sleep(3)
    tap(523, 1794)
    time.sleep(2)
    tap(871, 1958)
    time.sleep(2)
    tap(901, 1963)

devices = get_devices()

if not devices:
    print("❌ No authorized devices found")
else:
    print(f"✅ Found {len(devices)} devices:")
    for d in devices:
        print(" -", d)
        open_firefox(d)



    time.sleep(2)

    os.system(
        "adb shell am start -a android.intent.action.VIEW -d https://addons.mozilla.org/firefox/addon/cookie-editor org.mozilla.firefox"
    )

    time.sleep(2)

    tap(523, 1794)

    time.sleep(2)

    tap(871, 1958)

    time.sleep(2)







open_firefox()