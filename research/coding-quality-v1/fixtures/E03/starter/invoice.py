def subtotal(items):
    return sum(unit_cents for quantity, unit_cents in items)


def total(items, discount_cents):
    return subtotal(items) - discount_cents
