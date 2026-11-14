def to_seconds(config):
    """Return a copy with timeout_ms converted to timeout_s."""
    result = dict(config)
    if "timeout_ms" in result:
        if "timeout_s" in result:
            raise ValueError("both timeout_ms and timeout_s present")
        result["timeout_s"] = result.pop("timeout_ms") / 1000
    return result
