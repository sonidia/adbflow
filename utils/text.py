import base64

def normalize_text(s: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKC", s)
    s = s.casefold()
    s = s.replace("ı", "i")

    s = "".join(
        c for c in s
        if unicodedata.category(c) not in ("Mn", "Cf", "Cc")
    )

    return s

def detect_username_from_cookie_filename(filename: str) -> str:
    import re
    username = re.search(r'\[([^\]]+)\]\.(txt|json)$', filename, re.IGNORECASE)
    return normalize_text(username.group(1)) if username else ""

def to_base64(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")

def extract_tiktok_cookies(data: str) -> str:
    result = []

    for line in data.splitlines(True):
        s = line.strip()

        if not s or s.startswith("#"):
            result.append(line)
            continue

        parts = s.split()

        if len(parts) < 7:
            continue

        domain = parts[0].lower()

        if "tiktok" in domain:
            result.append(line)

    return "".join(result)

# def clean_text(s: str) -> str:
#     if not s:
#         return s
#     s = s.lstrip("\ufeff")
#     s = s.replace("\u200b", "").replace("\u200c", "").replace("\u200d", "")
#     return s

# def text(serial, t):
#     safe = t.replace(" ", "%s")
#     run_adb(serial, ["shell", "input", "text", safe])
