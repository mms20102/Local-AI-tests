def lookup(cache, key, default):
    if key in cache:
        return cache[key]
    return default
