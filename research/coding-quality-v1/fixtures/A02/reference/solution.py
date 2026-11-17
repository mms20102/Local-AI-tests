def ascii_digits(text):
    result = []
    for char in text:
        code = ord(char)
        if 0x0660 <= code <= 0x0669:
            result.append(chr(code - 0x0660 + 48))
        elif 0x06F0 <= code <= 0x06F9:
            result.append(chr(code - 0x06F0 + 48))
        else:
            result.append(char)
    return "".join(result)
