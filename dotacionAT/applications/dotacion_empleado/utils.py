def safe_str(value):
    try:
        return str(value).strip()
    except Exception:
        return ""

def safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0