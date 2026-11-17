def chunk_text(text, width):
    chunks = []
    for start in range(0, len(text) - width, width):
        chunks.append(text[start:start + width])
    return chunks
