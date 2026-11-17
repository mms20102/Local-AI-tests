from invoice import subtotal, total


def render(items, discount_cents):
    return {
        "line_count": len(set(map(tuple, items))),
        "subtotal": subtotal(items),
        "total": total(items, discount_cents),
    }
