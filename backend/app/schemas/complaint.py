from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProcessComplaintRequest(BaseModel):
    complaint_text: str
    current_form_data: Optional[dict] = None

class ComplaintExtractedData(BaseModel):
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    batch_number: Optional[str] = None
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    facility: Optional[str] = None
    impacted_material: Optional[str] = None
    complaint_category: Optional[str] = None
    raw_complaint_text: str
    qms_summary: Optional[str] = None
    suggested_severity: Optional[str] = None
    risk_assessment: Optional[str] = None
    recommended_action: Optional[str] = None
    copilot_message: Optional[str] = ""

class ComplaintCreate(BaseModel):
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    batch_number: Optional[str] = None
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    facility: Optional[str] = None
    impacted_material: Optional[str] = None
    complaint_category: Optional[str] = None
    raw_complaint_text: str
    qms_summary: Optional[str] = None
    suggested_severity: Optional[str] = None
    risk_assessment: Optional[str] = None
    recommended_action: Optional[str] = None
    status: Optional[str] = "Logged to QMS Ledger"

class ComplaintResponse(ComplaintCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
