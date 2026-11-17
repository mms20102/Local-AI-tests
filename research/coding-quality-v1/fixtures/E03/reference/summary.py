from invoice import subtotal, total


def render(items, discount_cents):
    return {
        "line_count": len(items),
        "subtotal_cents": subtotal(items),
        "total_cents": total(items, discount_cents),
    }
