def parse_kv(text):
    result = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            raise ValueError("missing =")
        key, value = stripped.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError("empty key")
        result[key] = value.strip()
    return result
