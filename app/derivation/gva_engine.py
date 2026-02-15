from collections import defaultdict


def reconstruct_gva(metrics):

    revenue_by_year = defaultdict(float)
    gva_by_year = {}

    for m in metrics:
        if m["metric_key"] == "revenue_eur" and m["year"]:
            revenue_by_year[m["year"]] += m["value"]

        if m["metric_key"] == "gross_value_added" and m["year"]:
            gva_by_year[m["year"]] = m["value"]

    derived_metrics = []

    for year, revenue in revenue_by_year.items():

        # If GVA not explicitly found, estimate at 50% of revenue
        if year not in gva_by_year:
            estimated_gva = revenue * 0.5

            derived_metrics.append({
                "document_id": metrics[0]["document_id"],
                "metric_key": "gross_value_added",
                "value": estimated_gva,
                "unit": "eur",
                "year": year,
                "source_type": "derived",
                "page_number": None,
                "confidence_score": 0.6,
                "raw_text": "Derived from revenue (estimated 50%)"
            })

    return derived_metrics
