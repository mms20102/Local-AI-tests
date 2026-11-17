import unicodedata


def ascii_digits(text):
    return "".join(str(unicodedata.digit(char)) if char.isdigit() else char for char in text)
