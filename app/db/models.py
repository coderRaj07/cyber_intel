from sqlalchemy import Column, Integer, String, Float, Text
from app.db.database import Base


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True)

    document_id = Column(String, index=True)
    metric_key = Column(String, index=True)

    value = Column(Float)
    unit = Column(String)

    year = Column(Integer)

    source_type = Column(String)
    page_number = Column(Integer)

    confidence_score = Column(Float)

    raw_text = Column(Text)


    category = Column(String, index=True)

    subcategory = Column(String, index=True)
    
    extraction_method = Column(String)
