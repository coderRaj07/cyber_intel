from pydantic import BaseModel

class MetricCreate(BaseModel):
    report_name: str
    metric_name: str
    value: float
    unit: str
    year: str
    page_number: int
    source_text: str
    confidence_score: float

class MetricResponse(MetricCreate):
    id: int

    class Config:
        orm_mode = True