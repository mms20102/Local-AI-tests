def chunk_text(text, width):
    if width <= 0:
        raise ValueError("width must be positive")
    return [text[start:start + width] for start in range(0, len(text), width)]
