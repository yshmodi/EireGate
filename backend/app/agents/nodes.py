from typing import Dict
from .state import EireGateState
from ..services.resume_parser import parse_resume
from ..services.resume_tailor import tailor_resume, calculate_match_score, generate_visa_advice
from langchain_core.messages import HumanMessage

def extract_node(state: EireGateState) -> Dict:
    parsed = parse_resume(state["raw_text"])
    return {
        "parsed_resume": parsed.model_dump(),
        "messages": [HumanMessage(content="Resume extracted and structured.")]
    }

def tailor_node(state: EireGateState) -> Dict:
    tailored = tailor_resume(
        state["parsed_resume"],
        state["target_role"],
        state["target_company"]
    )
    match_score = calculate_match_score(
        state["parsed_resume"].get("skills", []),
        tailored.key_skills
    )
    visa_advice = generate_visa_advice(state["parsed_resume"].get("education", []))

    return {
        "tailored_resume": tailored.model_dump(),
        "match_score": match_score,
        "visa_advice": visa_advice,
        "messages": [HumanMessage(content="Resume tailored + score & visa advice computed")]
    }

def visa_gap_node(state: EireGateState) -> Dict:
    # Placeholder expand later with salary parameters
    return {"messages": [HumanMessage(content="Visa gap analysis complete")]}
