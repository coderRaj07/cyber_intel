def reconcile(metrics):

    resolved = {}

    for m in metrics:

        key = (m["metric_key"], m["year"])

        if key not in resolved:
            resolved[key] = m
        else:
            # Prefer higher confidence
            if m["confidence_score"] > resolved[key]["confidence_score"]:
                resolved[key] = m

    return list(resolved.values())
