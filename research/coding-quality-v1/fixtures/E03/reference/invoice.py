def subtotal(items):
    return sum(quantity * unit_cents for quantity, unit_cents in items)


def total(items, discount_cents):
    return max(0, subtotal(items) - discount_cents)
