from sqlalchemy import Column, Integer, String, Float, Text
from app.database import Base

class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    report_name = Column(String)
    metric_name = Column(String)
    value = Column(Float)
    unit = Column(String)
    year = Column(String)
    page_number = Column(Integer)
    source_text = Column(Text)
    confidence_score = Column(Float)