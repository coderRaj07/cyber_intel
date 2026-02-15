from dataclasses import dataclass

@dataclass
class CanonicalMetric:
    document_id: str
    metric_key: str
    value: float
    unit: str
    year: int | None
    source_type: str
    page_number: int
    confidence_score: float
    raw_text: str | None
