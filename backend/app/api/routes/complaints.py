from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from pypdf import PdfReader
import io

from app.core.database import get_db
from app.models.complaint import ComplaintModel
from app.schemas.complaint import (
    ProcessComplaintRequest,
    ComplaintExtractedData,
    ComplaintCreate,
    ComplaintResponse
)
from langgraph_agent import process_complaint_workflow

router = APIRouter(prefix="/complaints", tags=["Complaints"])

@router.post("/process", response_model=ComplaintExtractedData)
def process_complaint(payload: ProcessComplaintRequest):
    """
    Passes raw complaint text through the LangGraph extraction pipeline.
    Returns structured data, QMS summary, risk assessment, severity, and recommended actions.
    """
    if not payload.complaint_text.strip():
        raise HTTPException(status_code=400, detail="Complaint text cannot be empty.")
    
    result = process_complaint_workflow(payload.complaint_text)
    
    return ComplaintExtractedData(
        customer_name=result.get("customer_name"),
        product_name=result.get("product_name"),
        batch_number=result.get("batch_number"),
        manufacturing_date=result.get("manufacturing_date"),
        expiry_date=result.get("expiry_date"),
        facility=result.get("facility"),
        impacted_material=result.get("impacted_material"),
        complaint_category=result.get("complaint_category"),
        raw_complaint_text=result.get("raw_text"),
        qms_summary=result.get("qms_summary"),
        suggested_severity=result.get("suggested_severity"),
        risk_assessment=result.get("risk_assessment"),
        recommended_action=result.get("recommended_action"),
        copilot_message=result.get("copilot_message")
    )

@router.post("/upload", response_model=ComplaintExtractedData)
async def upload_complaint_document(file: UploadFile = File(...)):
    """
    Processes an uploaded PDF or document, extracts text, and runs the LangGraph workflow.
    """
    try:
        contents = await file.read()
        extracted_text = ""
        
        if file.filename.endswith(".pdf"):
            pdf_reader = PdfReader(io.BytesIO(contents))
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
        else:
            extracted_text = contents.decode("utf-8", errors="ignore")
            
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="The uploaded document is empty or contains no readable text.")
            
        result = process_complaint_workflow(extracted_text)
        
        return ComplaintExtractedData(
            customer_name=result.get("customer_name"),
            product_name=result.get("product_name"),
            batch_number=result.get("batch_number"),
            manufacturing_date=result.get("manufacturing_date"),
            expiry_date=result.get("expiry_date"),
            facility=result.get("facility"),
            impacted_material=result.get("impacted_material"),
            complaint_category=result.get("complaint_category"),
            raw_complaint_text=extracted_text,
            qms_summary=result.get("qms_summary"),
            suggested_severity=result.get("suggested_severity"),
            risk_assessment=result.get("risk_assessment"),
            recommended_action=result.get("recommended_action"),
            copilot_message=result.get("copilot_message")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@router.post("/commit", response_model=ComplaintResponse)
def commit_complaint_to_ledger(payload: ComplaintCreate, db: Session = Depends(get_db)):
    """
    Saves the user-reviewed complaint record into the PostgreSQL / QMS Ledger database.
    """
    db_complaint = ComplaintModel(
        customer_name=payload.customer_name,
        product_name=payload.product_name,
        batch_number=payload.batch_number,
        manufacturing_date=payload.manufacturing_date,
        expiry_date=payload.expiry_date,
        facility=payload.facility,
        impacted_material=payload.impacted_material,
        complaint_category=payload.complaint_category,
        raw_complaint_text=payload.raw_complaint_text,
        qms_summary=payload.qms_summary,
        suggested_severity=payload.suggested_severity,
        risk_assessment=payload.risk_assessment,
        recommended_action=payload.recommended_action,
        status=payload.status or "Logged to QMS Ledger"
    )
    db.add(db_complaint)
    db.commit()
    db.refresh(db_complaint)
    return db_complaint

@router.get("", response_model=List[ComplaintResponse])
def get_complaints_ledger(db: Session = Depends(get_db)):
    """
    Retrieves all committed complaints stored in the QMS ledger database.
    """
    return db.query(ComplaintModel).order_by(ComplaintModel.id.desc()).all()
