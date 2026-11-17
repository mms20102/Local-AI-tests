def sliding_windows(values, size):
    windows = []
    for start in range(len(values) - size):
        windows.append(values[start:start + size])
    return windows
