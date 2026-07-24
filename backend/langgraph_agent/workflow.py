from langgraph.graph import StateGraph, END
from langgraph_agent.state import ComplaintState
from langgraph_agent.nodes import (
    extract_structured_data_node,
    generate_qms_summary_node,
    perform_risk_assessment_node,
    recommend_next_action_node
)

# Build the LangGraph workflow
workflow = StateGraph(ComplaintState)

# Add Nodes
workflow.add_node("extract_structured_data", extract_structured_data_node)
workflow.add_node("generate_qms_summary", generate_qms_summary_node)
workflow.add_node("perform_risk_assessment", perform_risk_assessment_node)
workflow.add_node("recommend_next_action", recommend_next_action_node)

# Define Directed Graph Edges
workflow.set_entry_point("extract_structured_data")
workflow.add_edge("extract_structured_data", "generate_qms_summary")
workflow.add_edge("generate_qms_summary", "perform_risk_assessment")
workflow.add_edge("perform_risk_assessment", "recommend_next_action")
workflow.add_edge("recommend_next_action", END)

# Compile Workflow
complaint_workflow = workflow.compile()

def process_complaint_workflow(raw_text: str) -> dict:
    """Executes the full LangGraph state graph pipeline."""
    initial_state = {
        "raw_text": raw_text,
        "customer_name": None,
        "product_name": None,
        "batch_number": None,
        "manufacturing_date": None,
        "expiry_date": None,
        "facility": None,
        "impacted_material": None,
        "complaint_category": None,
        "qms_summary": None,
        "suggested_severity": None,
        "risk_assessment": None,
        "recommended_action": None,
        "copilot_message": None
    }
    
    result = complaint_workflow.invoke(initial_state)
    return result
