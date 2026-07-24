import os
import re
import json
import logging
from langgraph_agent.state import ComplaintState

logger = logging.getLogger(__name__)

def _get_llm():
    api_key = os.getenv("GROQ_API_KEY", os.getenv("OPENAI_API_KEY", "")).strip()
    if not api_key:
        return None
    model_name = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
    
    # Try langchain_groq first
    try:
        from langchain_groq import ChatGroq
        return ChatGroq(groq_api_key=api_key, model_name=model_name, temperature=0.1)
    except Exception:
        pass

    # Fallback to OpenAI client pointing to Groq endpoint
    try:
        from langchain_openai import ChatOpenAI
        base_url = "https://api.groq.com/openai/v1" if api_key.startswith("gsk_") else None
        if base_url:
            return ChatOpenAI(api_key=api_key, base_url=base_url, model=model_name, temperature=0.1)
        return ChatOpenAI(api_key=api_key, model=model_name, temperature=0.1)
    except Exception as e:
        logger.warning(f"Could not initialize LLM with Groq/OpenAI: {e}")
        return None

def extract_structured_data_node(state: ComplaintState) -> ComplaintState:
    """Node 1: Extract structured parameters (Product, Batch, Dates, Customer, Facility, Category)."""
    text = state.get("raw_text", "").strip()
    text_lower = text.lower()
    
    # Check if text is a greeting or general query
    greetings = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening", "who are you", "help", "hi there", "hello there"]
    is_greeting = text_lower in greetings or len(text.split()) <= 2 and any(g in text_lower for g in ["hi", "hello", "hey"])

    if is_greeting:
        state.update({
            "customer_name": "Awaiting AI extraction...",
            "product_name": "Awaiting AI extraction...",
            "batch_number": "Awaiting AI extraction...",
            "manufacturing_date": "Awaiting AI extraction...",
            "expiry_date": "Awaiting AI extraction...",
            "facility": "Awaiting AI extraction...",
            "impacted_material": "Awaiting AI extraction...",
            "complaint_category": "Awaiting AI classification...",
            "qms_summary": "Awaiting AI extraction...",
            "suggested_severity": "Awaiting AI classification...",
            "risk_assessment": "Awaiting AI extraction...",
            "recommended_action": "Awaiting AI extraction...",
            "copilot_message": "Hello! 👋 I am your AI Copilot for pharmaceutical QMS complaint intake. Please paste a customer complaint or upload a report, and I will extract the metadata and auto-fill the form for you."
        })
        return state

    llm = _get_llm()
    
    extracted = {
        "customer_name": None,
        "product_name": None,
        "batch_number": None,
        "manufacturing_date": None,
        "expiry_date": None,
        "facility": None,
        "impacted_material": None,
        "complaint_category": None,
    }

    if llm:
        try:
            prompt = f"""
You are an expert pharmaceutical QMS AI Assistant. Extract structured information from this customer complaint.
Return ONLY valid JSON matching this schema:
{{
  "customer_name": "Customer or Pharmacy name or null",
  "product_name": "Full product name and strength or null",
  "batch_number": "Batch/Lot number or null",
  "manufacturing_date": "Manufacturing date string or null",
  "expiry_date": "Expiry date string or null",
  "facility": "Manufacturing or reporting facility or null",
  "impacted_material": "Packaging material/dosage form affected or null",
  "complaint_category": "Short standard category (e.g., Discolored capsules, Label error, Packaging defect, Shortage) or null"
}}

Complaint Text:
\"\"\"{text}\"\"\"
"""
            res = llm.invoke(prompt)
            content = res.content.strip()
            if content.startswith("```"):
                content = re.sub(r"^```[a-z]*\n?", "", content)
                content = re.sub(r"\n?```$", "", content)
            parsed = json.loads(content)
            extracted.update(parsed)
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}. Falling back to rule engine.")

    # Rule-based fallback/refinement engine for real complaints
    if not extracted.get("customer_name"):
        cust_match = re.search(r"([A-Z][a-zA-Z0-9\s&]+(?:Pharmacy|Hospital|Distributor|Clinic|Lab|Inc|Ltd))", text)
        if cust_match:
            extracted["customer_name"] = cust_match.group(1).strip()
        else:
            extracted["customer_name"] = "Direct Customer Report"

    if not extracted.get("product_name"):
        prod_match = re.search(r"\b([A-Z][a-zA-Z0-9\-]+\s+(?:Capsules|Tablets|Injection|Syrup|Suspension|Ointment)(?:\s+\d+\s*mg)?)\b", text)
        if prod_match and "discolored" not in prod_match.group(1).lower():
            extracted["product_name"] = prod_match.group(1).strip()
        else:
            prod_match2 = re.search(r"\b([A-Za-z0-9\-]+\s+(?:Capsules|Tablets|Injection|Syrup)(?:\s+\d+\s*mg)?)\b", text)
            if prod_match2 and "discolored" not in prod_match2.group(1).lower():
                extracted["product_name"] = prod_match2.group(1).strip()
            else:
                extracted["product_name"] = "Product details pending verification"

    if not extracted.get("batch_number"):
        batch_match = re.search(r"(?:Batch|Lot|B\.No\.?|Lot\.No\.?)\s*:?\s*([A-Z0-9\-]+)", text, re.IGNORECASE)
        if batch_match:
            extracted["batch_number"] = batch_match.group(1).strip()
        else:
            extracted["batch_number"] = "Not specified"

    if not extracted.get("manufacturing_date"):
        mfg_match = re.search(r"(?:Manufacturing|Mfg|MFD)(?:\s+date)?\s*:?\s*([A-Za-z0-9\s,/\-]+)", text, re.IGNORECASE)
        if mfg_match:
            extracted["manufacturing_date"] = mfg_match.group(1).strip()

    if not extracted.get("expiry_date"):
        exp_match = re.search(r"(?:Expiry|Exp|EXP)(?:\s+date)?\s*:?\s*([A-Za-z0-9\s,/\-]+)", text, re.IGNORECASE)
        if exp_match:
            extracted["expiry_date"] = exp_match.group(1).strip()

    if not extracted.get("complaint_category"):
        if "discolor" in text_lower or "color" in text_lower:
            extracted["complaint_category"] = "Discolored capsules"
        elif "leak" in text_lower or "broken" in text_lower or "seal" in text_lower:
            extracted["complaint_category"] = "Packaging defect"
        elif "contamination" in text_lower or "particle" in text_lower:
            extracted["complaint_category"] = "Foreign particulate matter"
        else:
            extracted["complaint_category"] = "Product Quality Defect"

    if not extracted.get("facility"):
        extracted["facility"] = "Main Manufacturing Facility"
        
    if not extracted.get("impacted_material"):
        if "capsule" in text_lower:
            extracted["impacted_material"] = "Hard Gelatin Capsule Shell"
        else:
            extracted["impacted_material"] = "Primary Packaging Container"

    state.update({
        "customer_name": extracted.get("customer_name") or "Direct Customer Report",
        "product_name": extracted.get("product_name") or "Product details pending verification",
        "batch_number": extracted.get("batch_number") or "Not specified",
        "manufacturing_date": extracted.get("manufacturing_date") or "Not specified",
        "expiry_date": extracted.get("expiry_date") or "Not specified",
        "facility": extracted.get("facility") or "Main Manufacturing Facility",
        "impacted_material": extracted.get("impacted_material") or "Primary Packaging Container",
        "complaint_category": extracted.get("complaint_category") or "Product Quality Defect",
    })
    return state

def generate_qms_summary_node(state: ComplaintState) -> ComplaintState:
    """Node 2: Rewrite informal text into formal QMS description."""
    if state.get("copilot_message") and "Hello!" in state.get("copilot_message"):
        return state

    text = state.get("raw_text", "")
    customer = state.get("customer_name", "Customer")
    product = state.get("product_name", "Product")
    category = state.get("complaint_category", "Quality Defect")
    
    llm = _get_llm()
    summary = None

    if llm:
        try:
            prompt = f"Rewrite this customer complaint into a concise, professional Quality Management System (QMS) complaint summary for pharmaceutical documentation:\n\n{text}"
            res = llm.invoke(prompt)
            summary = res.content.strip()
        except Exception:
            pass

    if not summary:
        summary = f"{customer} reported an issue categorized as '{category}' regarding {product}. Requesting formal investigation, batch verification, and appropriate corrective action/replacement."

    state["qms_summary"] = summary
    return state

def perform_risk_assessment_node(state: ComplaintState) -> ComplaintState:
    """Node 3: Assess root cause risk and determine severity (Minor, Major, Critical)."""
    if state.get("copilot_message") and "Hello!" in state.get("copilot_message"):
        return state

    text = state.get("raw_text", "").lower()
    category = state.get("complaint_category", "").lower()
    llm = _get_llm()
    
    severity = "Major"
    risk = "Potential primary packaging seal failure or environmental humidity exposure leading to physical/chemical degradation during storage or transit."

    if "death" in text or "anaphylaxis" in text or "severe injury" in text or "toxic" in text:
        severity = "Critical"
        risk = "Potential high-risk safety hazard. High probability of adverse clinical outcomes or contamination."
    elif "discolor" in text or "capsule" in category:
        severity = "Major"
        risk = "Potential moisture ingress or primary packaging seal failure leading to capsule discoloration and physical degradation."
    elif "label" in text or "typo" in text:
        severity = "Minor"
        risk = "Cosmetic/labeling error without direct impact on product efficacy or patient safety."

    if llm:
        try:
            prompt = f"Perform a QMS Risk Assessment for the following complaint. Return JSON with keys 'severity' (Minor, Major, or Critical) and 'risk_assessment' (detailed engineering/quality risk description):\n\nComplaint: {text}"
            res = llm.invoke(prompt)
            content = res.content.strip()
            if content.startswith("```"):
                content = re.sub(r"^```[a-z]*\n?", "", content)
                content = re.sub(r"\n?```$", "", content)
            parsed = json.loads(content)
            severity = parsed.get("severity", severity)
            risk = parsed.get("risk_assessment", risk)
        except Exception:
            pass

    state["suggested_severity"] = severity
    state["risk_assessment"] = risk
    return state

def recommend_next_action_node(state: ComplaintState) -> ComplaintState:
    """Node 4: Recommend standard QMS SOP action."""
    if state.get("copilot_message") and "Hello!" in state.get("copilot_message"):
        return state

    severity = state.get("suggested_severity", "Major")
    
    if severity == "Critical":
        action = "Immediate Quarantine of Batch + Route to QA Senior Director + Initiate Urgent Recall Assessment & Health Hazard Evaluation."
    elif severity == "Major":
        action = "Route to QA Investigation & Issue Product Replacement. Initiate Retain Sample Testing & Environmental Stability Audit."
    else:
        action = "Log in QMS Ledger + Route to Packaging Operations for Routine Review."

    message = (
        f"Complaint parsed successfully. I've extracted product details ({state.get('product_name')}), "
        f"mapped batch information ({state.get('batch_number')}), assigned a severity rating of '{severity}', "
        f"and generated an initial risk assessment."
    )

    state["recommended_action"] = action
    state["copilot_message"] = message
    return state

