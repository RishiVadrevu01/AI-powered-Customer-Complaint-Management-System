from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.core.database import Base

class ComplaintModel(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_name = Column(String(255), nullable=True)
    product_name = Column(String(255), nullable=True)
    batch_number = Column(String(255), nullable=True)
    manufacturing_date = Column(String(100), nullable=True)
    expiry_date = Column(String(100), nullable=True)
    facility = Column(String(255), nullable=True)
    impacted_material = Column(String(255), nullable=True)
    complaint_category = Column(String(255), nullable=True)
    raw_complaint_text = Column(Text, nullable=False)
    qms_summary = Column(Text, nullable=True)
    suggested_severity = Column(String(50), nullable=True) # Minor, Major, Critical
    risk_assessment = Column(Text, nullable=True)
    recommended_action = Column(Text, nullable=True)
    status = Column(String(50), default="Logged to QMS Ledger")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
