def parse_kv(text):
    result = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split("=")
        if len(parts) < 2:
            raise ValueError("missing =")
        result[parts[0].strip()] = parts[1].strip()
    return result
