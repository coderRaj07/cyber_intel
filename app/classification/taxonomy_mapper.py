from app.schema.taxonomy import CANONICAL_TAXONOMY


def map_to_taxonomy(metric):

    key = metric["metric_key"]

    if key in CANONICAL_TAXONOMY:
        metric["unit"] = CANONICAL_TAXONOMY[key]["unit"]
        metric["category"] = CANONICAL_TAXONOMY[key]["category"]

    return metric
