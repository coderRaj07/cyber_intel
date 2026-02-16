import json
import re
from app.services.llm_client import call_cerebras
def numeric_exists_in_text(value, original_text):
    """
    Strict numeric token validation.
    Only accept exact numeric tokens present in text.
    """

    if value is None:
        return False

    # Extract all numeric tokens from original text
    tokens = re.findall(r"\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b", original_text)

    normalized_tokens = [t.replace(",", "") for t in tokens]
    normalized_value = str(value).replace(",", "")

    return normalized_value in normalized_tokens

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
        metric_name = m.get("metric_name", "")
        unit = m.get("unit", "")

        # 1️⃣ Must exist exactly in original block
        if not numeric_exists_in_text(value, block_text):
            continue

        # 2️⃣ Reject very small standalone numbers without economic context
        if isinstance(value, (int, float)):
            if value < 10 and unit not in ["%", "percent"]:
                continue

        # 3️⃣ Reject if source sentence too short (likely header/numbering)
        if len(source_text.split()) < 6:
            continue

        # 4️⃣ Must contain economic keywords
        economic_keywords = [
            "firm", "employment", "revenue", "gva",
            "professional", "office", "growth",
            "percentage", "investment", "salary",
            "forecast", "sector", "cyber"
        ]

        if not any(word in source_text.lower() for word in economic_keywords):
            continue

        try:
            value = float(str(value).replace(",", ""))
        except:
            continue

        validated_metrics.append({
            "report_name": report_name,
            "metric_name": metric_name,
            "value": value,
            "unit": unit,
            "year": m.get("year"),
            "page_number": page_number,
            "source_text": source_text,
            "confidence_score": 1.0
        })

    return validated_metrics