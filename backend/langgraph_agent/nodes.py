import os
import re
import json
import logging
from typing import Optional
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

def _clean_field_value(val: Optional[str]) -> Optional[str]:

    if not val or not isinstance(val, str):
        return val
    # Remove leading conversational filler words (e.g. "is November 2028" -> "November 2028")
    cleaned = re.sub(r"^(?:is|was|should\s+be|to\s+be|set\s+to|date\s+is|the\s+expiry\s+date\s+is|expiry\s+is|mfg\s+is|batch\s+is|number\s+is|are)\s+", "", val.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"^(?:is|was|are)\s+", "", cleaned.strip(), flags=re.IGNORECASE)
    cleaned = cleaned.strip('".\' ')
    return cleaned

def extract_structured_data_node(state: ComplaintState) -> ComplaintState:
    """Node 1: Extract structured parameters (Product, Batch, Dates, Customer, Facility, Category)."""
    text = state.get("raw_text", "").strip()
    existing = state.get("existing_form_data") or {}
    text_lower = text.lower()
    
    # Check if text is a greeting or general query
    greetings = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening", "who are you", "help", "hi there", "hello there"]
    is_greeting = text_lower in greetings or len(text.split()) <= 2 and any(g in text_lower for g in ["hi", "hello", "hey"])

    if is_greeting and not existing:
        state.update({
            "customer_name": "",
            "product_name": "",
            "batch_number": "",
            "manufacturing_date": "",
            "expiry_date": "",
            "facility": "",
            "impacted_material": "",
            "complaint_category": "",
            "qms_summary": "",
            "suggested_severity": "",
            "risk_assessment": "",
            "recommended_action": "",
            "copilot_message": "Hello! 👋 I am your AI Copilot for pharmaceutical QMS complaint intake. Please paste a customer complaint or upload a report, and I will extract the metadata and auto-fill the form for you."
        })
        return state

    llm = _get_llm()
    has_existing = bool(existing.get("product_name") and existing.get("product_name") != "Product details pending verification")
    
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
            if has_existing:
                prompt = f"""
You are an expert pharmaceutical QMS AI Assistant updating an existing complaint form.

Current Form Data:
{json.dumps(existing, indent=2)}

New User Prompt / Correction:
\"\"\"{text}\"\"\"

Instructions:
1. Identify if the user prompt is a correction, update, or addition (e.g. 'Correction: batch number should be AMX-9982-X and expiry is Nov 2028').
2. Extract the NEW or CORRECTED field values for any mentioned parameters.
3. For any fields NOT mentioned or unchanged in the new user prompt, PRESERVE their exact current value from Current Form Data.

Return ONLY valid JSON matching this schema:
{{
  "customer_name": "Updated customer or current value",
  "product_name": "Updated product or current value",
  "batch_number": "Updated batch number or current value",
  "manufacturing_date": "Updated mfg date or current value",
  "expiry_date": "Updated exp date or current value",
  "facility": "Updated facility or current value",
  "impacted_material": "Updated impacted material or current value",
  "complaint_category": "Updated complaint category or current value"
}}
"""
            else:
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

    # Rule-based fallback/refinement engine
    if not extracted.get("customer_name"):
        cust_match = re.search(r"([A-Z][a-zA-Z0-9\s&]+(?:Pharmacy|Hospital|Distributor|Clinic|Lab|Inc|Ltd))", text)
        if cust_match:
            extracted["customer_name"] = cust_match.group(1).strip()
        elif has_existing and existing.get("customer_name"):
            extracted["customer_name"] = existing.get("customer_name")
        else:
            extracted["customer_name"] = "Direct Customer Report"

    if not extracted.get("product_name"):
        prod_match = re.search(r"\b([A-Z][a-zA-Z0-9\-]+\s+(?:Capsules|Tablets|Injection|Syrup|Suspension|Ointment)(?:\s+\d+\s*mg)?)\b", text)
        if prod_match and "discolored" not in prod_match.group(1).lower():
            extracted["product_name"] = prod_match.group(1).strip()
        elif has_existing and existing.get("product_name"):
            extracted["product_name"] = existing.get("product_name")
        else:
            extracted["product_name"] = "Product details pending verification"

    if not extracted.get("batch_number"):
        batch_match = re.search(r"(?:batch|lot|b\.no\.?|lot\.no\.?)(?:\s+(?:number|no\.?))?(?:\s+(?:is|was|actually|should\s+be))*\s*:?\s*([A-Z0-9\-]{3,})", text, re.IGNORECASE)
        if batch_match:
            extracted["batch_number"] = batch_match.group(1).strip()
        elif has_existing and existing.get("batch_number"):
            extracted["batch_number"] = existing.get("batch_number")
        else:
            extracted["batch_number"] = "Not specified"

    date_regex = r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})"

    if not extracted.get("manufacturing_date"):
        mfg_match = re.search(r"(?:manufacturing|mfg|mfd)(?:\s+(?:date|data))?(?:\s+(?:is|was|actually|should\s+be))*\s*:?\s*" + date_regex, text, re.IGNORECASE)
        if mfg_match:
            extracted["manufacturing_date"] = mfg_match.group(1).strip()
        elif has_existing and existing.get("manufacturing_date"):
            extracted["manufacturing_date"] = existing.get("manufacturing_date")

    if not extracted.get("expiry_date"):
        exp_match = re.search(r"(?:expiring|expiry|exp)(?:\s+(?:date|data))?(?:\s+(?:is|was|actually|should\s+be))*\s*:?\s*" + date_regex, text, re.IGNORECASE)
        if exp_match:
            extracted["expiry_date"] = exp_match.group(1).strip()
        elif has_existing and existing.get("expiry_date"):
            extracted["expiry_date"] = existing.get("expiry_date")

    if not extracted.get("complaint_category"):
        if "discolor" in text_lower or "color" in text_lower:
            extracted["complaint_category"] = "Discolored capsules"
        elif "leak" in text_lower or "broken" in text_lower or "seal" in text_lower:
            extracted["complaint_category"] = "Packaging defect"
        elif "contamination" in text_lower or "particle" in text_lower:
            extracted["complaint_category"] = "Foreign particulate matter"
        elif has_existing and existing.get("complaint_category"):
            extracted["complaint_category"] = existing.get("complaint_category")
        else:
            extracted["complaint_category"] = "Product Quality Defect"

    if not extracted.get("facility"):
        if has_existing and existing.get("facility"):
            extracted["facility"] = existing.get("facility")
        else:
            extracted["facility"] = "Main Manufacturing Facility"
        
    if not extracted.get("impacted_material"):
        if "capsule" in text_lower:
            extracted["impacted_material"] = "Hard Gelatin Capsule Shell"
        elif has_existing and existing.get("impacted_material"):
            extracted["impacted_material"] = existing.get("impacted_material")
        else:
            extracted["impacted_material"] = "Primary Packaging Container"

    # Clean filler words from extracted values
    for k in extracted:
        if extracted[k]:
            extracted[k] = _clean_field_value(extracted[k])

    # Merge preservation pass: guarantee no existing field is overwritten by a generic placeholder
    if has_existing:
        for k in ["customer_name", "product_name", "batch_number", "manufacturing_date", "expiry_date", "facility", "impacted_material", "complaint_category"]:
            val = extracted.get(k)
            ex_val = existing.get(k)
            if ex_val and ex_val not in ["Product details pending verification", "Not specified", "Direct Customer Report", "Main Manufacturing Facility", "Primary Packaging Container", "Product Quality Defect", ""]:
                if not val or val in ["Product details pending verification", "Not specified", "Direct Customer Report", "Main Manufacturing Facility", "Primary Packaging Container", "Product Quality Defect", ""]:
                    extracted[k] = ex_val

    state.update({
        "customer_name": _clean_field_value(extracted.get("customer_name")) or (existing.get("customer_name") if has_existing else "Direct Customer Report"),
        "product_name": _clean_field_value(extracted.get("product_name")) or (existing.get("product_name") if has_existing else "Product details pending verification"),
        "batch_number": _clean_field_value(extracted.get("batch_number")) or (existing.get("batch_number") if has_existing else "Not specified"),
        "manufacturing_date": _clean_field_value(extracted.get("manufacturing_date")) or (existing.get("manufacturing_date") if has_existing else "Not specified"),
        "expiry_date": _clean_field_value(extracted.get("expiry_date")) or (existing.get("expiry_date") if has_existing else "Not specified"),
        "facility": _clean_field_value(extracted.get("facility")) or (existing.get("facility") if has_existing else "Main Manufacturing Facility"),
        "impacted_material": _clean_field_value(extracted.get("impacted_material")) or (existing.get("impacted_material") if has_existing else "Primary Packaging Container"),
        "complaint_category": _clean_field_value(extracted.get("complaint_category")) or (existing.get("complaint_category") if has_existing else "Product Quality Defect"),
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
    batch = state.get("batch_number", "")
    
    llm = _get_llm()
    summary = None

    if llm:
        try:
            prompt = (
                f"Rewrite this customer complaint into a concise, professional Quality Management System (QMS) "
                f"complaint summary for pharmaceutical documentation. "
                f"Customer: {customer}, Product: {product}, Batch: {batch}, Category: {category}.\n"
                f"User Prompt / Input: {text}\n"
                f"Do NOT use markdown bold syntax, headers, or asterisks (**). Output plain clean text only."
            )
            res = llm.invoke(prompt)
            summary = res.content.strip()
        except Exception:
            pass

    if not summary:
        summary = f"{customer} reported an issue categorized as '{category}' regarding {product} (Batch: {batch}). Requesting formal investigation, batch verification, and appropriate corrective action/replacement."

    # Sanitize markdown asterisks from summary
    summary = re.sub(r'\*+', '', summary).strip()

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
            prompt = f"Perform a QMS Risk Assessment for the following complaint. Return JSON with keys 'severity' (Minor, Major, or Critical) and 'risk_assessment' (detailed engineering/quality risk description without markdown asterisks):\n\nComplaint: {text}"
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

    # Sanitize markdown asterisks from risk
    risk = re.sub(r'\*+', '', risk).strip()

    state["suggested_severity"] = severity
    state["risk_assessment"] = risk
    return state

def recommend_next_action_node(state: ComplaintState) -> ComplaintState:
    """Node 4: Recommend standard QMS SOP action."""
    if state.get("copilot_message") and "Hello!" in state.get("copilot_message"):
        return state

    severity = state.get("suggested_severity", "Major")
    has_existing = bool(state.get("existing_form_data") and state.get("existing_form_data").get("product_name") and state.get("existing_form_data").get("product_name") != "Product details pending verification")

    action = None
    llm = _get_llm()
    if llm:
        try:
            prompt = (
                f"Given a pharmaceutical complaint with severity '{severity}', recommend a concise, standard QMS next action step or SOP. "
                f"Do not use markdown formatting. Keep it to 1-2 sentences.\n"
                f"Complaint summary: {state.get('qms_summary')}"
            )
            res = llm.invoke(prompt)
            action = res.content.strip()
            action = re.sub(r'\*+', '', action).strip()
        except Exception as e:
            logger.warning(f"Failed to generate action with LLM: {e}")
            pass

    if not action:
        if severity == "Critical":
            action = "Immediate Quarantine of Batch + Route to QA Senior Director + Initiate Urgent Recall Assessment & Health Hazard Evaluation."
        elif severity == "Major":
            action = "Route to QA Investigation & Issue Product Replacement. Initiate Retain Sample Testing & Environmental Stability Audit."
        else:
            action = "Log in QMS Ledger + Route to Packaging Operations for Routine Review."

    if has_existing:
        message = (
            f"Form updated with specified corrections! Updated batch/expiry information "
            f"(Batch: {state.get('batch_number')}, Expiry: {state.get('expiry_date')}). "
            f"All existing product metadata preserved."
        )
    else:
        message = (
            f"Complaint parsed successfully. I've extracted product details ({state.get('product_name')}), "
            f"mapped batch information ({state.get('batch_number')}), assigned a severity rating of '{severity}', "
            f"and generated an initial risk assessment."
        )

    state["recommended_action"] = action
    state["copilot_message"] = message
    return state

