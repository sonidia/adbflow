import subprocess, zipfile, tempfile, os, json, shutil

si = subprocess.STARTUPINFO()
si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

def adb(serial, *args, check=True):
    result = subprocess.run(
        ["adb", "-s", serial, *args],
        startupinfo=si,
        check=False,
        capture_output=True,
        text=True
    )
    if check and result.returncode != 0:
        err = (result.stderr or result.stdout or "unknown error").strip()
        raise RuntimeError(err)
    return result

def adb_output(serial, *args):
    result = subprocess.run(
        ["adb", "-s", serial, *args],
        startupinfo=si,
        check=True,
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def setup_adb_keyboard(
    serial: str,
    apk_path: str = "keyboard.apk",
    ime: str = "com.android.adbkeyboard/.AdbIME"
):
    adb(serial, "install", "-r", apk_path)
    adb(serial, "shell", "ime", "enable", ime)
    adb(serial, "shell", "ime", "set", ime)

def install_xapk(serial: str, xapk_path: str):
    """
    Install a .xapk or .apkm file to a device.
    - XAPK (APKPure): manifest.json with "split_apks" list
    - APKM (APKMirror): info.json with "pname", all split_*.apk + base.apk files
    """
    tmp_dir = tempfile.mkdtemp(prefix="xapk_")
    try:
        # --- Extract archive ---
        with zipfile.ZipFile(xapk_path, "r") as z:
            z.extractall(tmp_dir)

        package_name = None
        split_apk_files = []
        ext = os.path.splitext(xapk_path)[1].lower()

        if ext == ".apkm":
            # --- APKM format (APKMirror): info.json, all .apk files are splits ---
            info_path = os.path.join(tmp_dir, "info.json")
            if os.path.isfile(info_path):
                with open(info_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                package_name = data.get("pname") or data.get("package_name")
            # Collect all .apk files (base.apk + split_*.apk)
            for fname in os.listdir(tmp_dir):
                if fname.lower().endswith(".apk"):
                    split_apk_files.append(os.path.join(tmp_dir, fname))

        else:
            # --- XAPK format (APKPure): manifest.json with explicit split_apks list ---
            manifest_path = os.path.join(tmp_dir, "manifest.json")
            if os.path.isfile(manifest_path):
                with open(manifest_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                package_name = data.get("package_name")
                for entry in data.get("split_apks", []):
                    fpath = os.path.join(tmp_dir, entry["file"])
                    if os.path.isfile(fpath):
                        split_apk_files.append(fpath)

        # Fallback: scan all .apk if still empty
        if not split_apk_files:
            for root, _, files in os.walk(tmp_dir):
                for fname in files:
                    if fname.lower().endswith(".apk"):
                        split_apk_files.append(os.path.join(root, fname))

        if not split_apk_files:
            raise FileNotFoundError(f"No APK files found inside {xapk_path}")

        # --- Install split APKs ---
        adb(serial, "install-multiple", "-r", *split_apk_files)

        # --- Push OBB files if any ---
        for root, _, files in os.walk(tmp_dir):
            for fname in files:
                if fname.lower().endswith(".obb"):
                    src = os.path.join(root, fname)
                    remote_dir = f"/sdcard/Android/obb/{package_name}" if package_name else "/sdcard"
                    adb(serial, "shell", "mkdir", "-p", remote_dir, check=False)
                    adb(serial, "push", src, f"{remote_dir}/{fname}")

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

def install_chrome(serial: str, apk_path: str = "chrome.apkm"):
    ext = os.path.splitext(apk_path)[1].lower()
    if ext in (".xapk", ".apkm"):
        install_xapk(serial, apk_path)
    else:
        adb(serial, "install", "-r", apk_path)

def open_url_in_chrome(serial: str, url: str):
    """Mở Chrome trên device và điều hướng tới URL."""
    if not url:
        raise ValueError("URL is empty")
    # Đảm bảo có scheme
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    adb(serial, "shell", "am", "start",
        "-a", "android.intent.action.VIEW",
        "-n", "com.android.chrome/com.google.android.apps.chrome.Main",
        "-d", url)

def run_ads_automation(
    serial: str,
    url: str,
):
    """
    Mở link ads trong Chrome rồi dùng CDP để thao tác DOM.

    Args:
        serial: ADB serial của device
        url: link ads cần mở

    Raises:
        RuntimeError: nếu Chrome không chạy hoặc lỗi kết nối
    """
    from utils.cdp_chrome import ChromeCDP

    with ChromeCDP(serial=serial, initial_url=url) as cdp:

        # Đợi trang load
        import time
        time.sleep(5)

        # Đợi modal "Link to ad" xuất hiện (tìm cả trong iframes)
        print(f"⏳ Waiting for 'Link to ad' modal on {serial}...")
        modal_appeared = False
        for _ in range(15):  # Đợi tối đa 15 giây
            time.sleep(1)
            check_modal = cdp.execute_js("""
            (function() {
                // Tìm đúng dialog chứa text "Link to ad"
                const dialogs = document.querySelectorAll('[role="dialog"]');
                for (const dialog of dialogs) {
                    if (dialog.textContent && dialog.textContent.toLowerCase().includes('link to ad')) {
                        return true;
                    }
                }
                return false;
            })()
            """)
            if check_modal:
                modal_appeared = True
                print(f"✅ 'Link to ad' modal appeared on {serial}")
                break

        if not modal_appeared:
            print(f"⚠️  'Link to ad' modal not found on {serial}")
            page_title = cdp.get_page_title()
            return page_title

        # Cuộn xuống trong modal để nút "Learn more" hiện ra
        print(f"📜 Scrolling down in modal to find 'Learn more' button on {serial}...")
        cdp.execute_js("""
        (function() {
            // Cuộn đúng dialog chứa "link to ad"
            const dialogs = document.querySelectorAll('[role="dialog"]');
            for (const dialog of dialogs) {
                if (dialog.textContent && dialog.textContent.toLowerCase().includes('link to ad')) {
                    dialog.scrollTop = dialog.scrollHeight;
                    return;
                }
            }
            window.scrollTo(0, document.body.scrollHeight);
        })()
        """)
        time.sleep(1)

        # Tìm và click button "Learn more" trong modal
        try:
            # Lấy tọa độ của button "Learn more" trong dialog
            js_rect = """
            (function() {
                const dialogs = document.querySelectorAll('[role="dialog"]');
                let targetDialog = null;
                for (const dialog of dialogs) {
                    if (dialog.textContent && dialog.textContent.toLowerCase().includes('link to ad')) {
                        targetDialog = dialog;
                        break;
                    }
                }
                if (!targetDialog) return null;

                const btn = Array.from(targetDialog.querySelectorAll('a, button, [role="button"]')).find(el =>
                    el.textContent && el.textContent.trim().toLowerCase().includes('learn more')
                );
                if (!btn) return null;

                btn.scrollIntoView({block: 'center'});
                const rect = btn.getBoundingClientRect();
                return {
                    x: Math.round(rect.left + rect.width / 2),
                    y: Math.round(rect.top + rect.height / 2)
                };
            })()
            """
            rect = cdp.execute_js(js_rect)
            if rect and rect.get('x') and rect.get('y'):
                x, y = rect['x'], rect['y']
                print(f"🎯 'Learn more' button found at ({x}, {y}) on {serial}")
                # Dùng CDP Input để click tọa độ thật
                cdp._send_command("Input.dispatchMouseEvent", {
                    "type": "mousePressed", "x": x, "y": y,
                    "button": "left", "clickCount": 1
                })
                time.sleep(0.1)
                cdp._send_command("Input.dispatchMouseEvent", {
                    "type": "mouseReleased", "x": x, "y": y,
                    "button": "left", "clickCount": 1
                })
                print(f"✅ Clicked 'Learn more' button in modal on {serial}")
                # Đợi trang đích load
                time.sleep(5)
                page_title = cdp.get_page_title()
                page_url = cdp.get_current_url()
                print(f"📄 Landed on: {page_title} ({page_url})")
            else:
                print(f"⚠️  'Learn more' button not found in modal on {serial}")
                page_title = cdp.get_page_title()
                page_url = cdp.get_current_url()
        except Exception as e:
            print(f"⚠️  Error clicking 'Learn more' in modal on {serial}: {e}")
            page_title = cdp.get_page_title()
            page_url = cdp.get_current_url()

        # ----------------------------------------------------------------
        # Có thể thêm logic khác tại đây nếu cần
        # ----------------------------------------------------------------

        # Lấy domain từ URL
        from urllib.parse import urlparse
        domain = urlparse(page_url).netloc if page_url else ""

        return {"title": page_title, "domain": domain, "url": page_url}
