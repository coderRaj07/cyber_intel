def compute_confidence(source_text: str) -> float:

    score = 0.8

    if "%" in source_text:
        score += 0.05

    if "€" in source_text or "£" in source_text:
        score += 0.05

    if len(source_text) > 50:
        score += 0.05

    return min(score, 0.99)