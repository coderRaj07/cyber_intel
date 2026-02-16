import json
import re
from app.services.llm_client import call_cerebras


def numeric_exists_in_text(value, original_text):
    """
    Prevent hallucinations by ensuring extracted number
    exists exactly in original text.
    """

    if value is None:
        return False

    # Normalize
    normalized_text = original_text.replace(",", "")
    normalized_value = str(value).replace(",", "")

    return normalized_value in normalized_text


def extract_metrics(block_text: str, page_number: int, report_name: str):

    prompt = f"""
        You are a STRICT data extraction engine.

        TASK:
        Extract ALL quantitative metrics explicitly written in the text.

        STRICT RULES:
        1. DO NOT infer.
        2. DO NOT calculate derived values.
        3. DO NOT round numbers.
        4. DO NOT modify numbers.
        5. DO NOT guess missing years.
        6. If a year is not explicitly mentioned in the same sentence, set year = null.
        7. Extract ONLY numbers that appear exactly in the text.
        8. Do NOT compute revenue per employee or similar derived metrics.

        Return ONLY valid JSON array.

        Each object must contain:
        - metric_name
        - value
        - unit
        - year (null if not explicitly present)
        - source_text (exact sentence containing number)

        TEXT:
        {block_text}
        """

    response = call_cerebras(prompt)

    try:
        metrics = json.loads(response)
    except:
        return []

    validated_metrics = []

    for m in metrics:
        value = m.get("value")
        source_text = m.get("source_text", "")

        # Validate numeric anchor
        if not numeric_exists_in_text(value, block_text):
            continue

        try:
            value = float(str(value).replace(",", ""))
        except:
            continue

        validated_metrics.append({
            "report_name": report_name,
            "metric_name": m.get("metric_name"),
            "value": value,
            "unit": m.get("unit"),
            "year": m.get("year"),
            "page_number": page_number,
            "source_text": source_text,
            "confidence_score": 1.0  # exact anchor match
        })

    return validated_metrics