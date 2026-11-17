def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def sign(value):
    return (value > 0) - (value < 0)


def is_even(value):
    return value % 2 == 0


def first_or_none(values):
    return values[0] if values else None


def last_or_none(values):
    return values[-1] if values else None


def count_nonempty(values):
    return sum(1 for value in values if len(value) > 0)


def reverse_text(text):
    return text[::-1]
