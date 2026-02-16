def normalize_value(value, unit):
    if unit == "EUR":
        return value * 1_000_000_000
    return value