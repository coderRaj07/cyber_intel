def compute_confidence(metric, similarity_score=None):

    base = 0.6

    if metric["source_type"] == "table":
        base += 0.2

    if metric["source_type"] == "chart_vector":
        base += 0.15

    if similarity_score:
        base += 0.2 * similarity_score

    if metric.get("year"):
        base += 0.05

    return min(base, 1.0)
