from typing import TypedDict, Optional

class ComplaintState(TypedDict):
    raw_text: str
    existing_form_data: Optional[dict]
    customer_name: Optional[str]
    product_name: Optional[str]
    batch_number: Optional[str]
    manufacturing_date: Optional[str]
    expiry_date: Optional[str]
    facility: Optional[str]
    impacted_material: Optional[str]
    complaint_category: Optional[str]
    qms_summary: Optional[str]
    suggested_severity: Optional[str]
    risk_assessment: Optional[str]
    recommended_action: Optional[str]
    copilot_message: Optional[str]
