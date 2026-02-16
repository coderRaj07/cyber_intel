import json
from app.services.llm_client import call_cerebras
from app.services.confidence import compute_confidence


def extract_metrics(text: str, page: int, report_name: str):

    prompt = f"""
    Extract ALL explicit quantitative metrics.

    Rules:
    - Extract ONLY numbers explicitly written.
    - Do NOT infer.
    - Return ONLY valid JSON array.
    - Each object must contain:
        metric_name
        value
        unit
        year (if present)
        source_text (exact sentence containing the metric)

    Text:
    {text}
    """

    response = call_cerebras(prompt)

    try:
        parsed = json.loads(response)
    except:
        return []  # No hallucination allowed

    results = []

    for m in parsed:

        try:
            value = float(str(m["value"]).replace(",", ""))
        except:
            continue

        confidence = compute_confidence(m["source_text"])

        results.append({
            "report_name": report_name,
            "metric_name": m["metric_name"],
            "value": value,
            "unit": m["unit"],
            "year": m.get("year", ""),
            "page_number": page,
            "source_text": m["source_text"],
            "confidence_score": confidence
        })

    return results