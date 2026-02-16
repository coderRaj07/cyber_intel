from sqlalchemy import Column, Integer, String, Float, Text
from app.database import Base


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)

    report_name = Column(String, nullable=False)

    metric_name = Column(String, nullable=False)

    value = Column(Float, nullable=False)

    unit = Column(String)

    year = Column(String, nullable=True)

    page_number = Column(Integer, nullable=False)

    source_text = Column(Text, nullable=False)

    confidence_score = Column(Float, nullable=False)