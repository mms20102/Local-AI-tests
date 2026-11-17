def sliding_windows(values, size):
    if size <= 0:
        raise ValueError("size must be positive")
    return [values[start:start + size] for start in range(len(values) - size + 1)]
