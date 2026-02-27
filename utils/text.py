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
#     return s

# def text(serial, t):
#     safe = t.replace(" ", "%s")
#     run_adb(serial, ["shell", "input", "text", safe])
