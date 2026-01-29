from typing import TypedDict, Annotated, List, Dict
from langchain_core.messages import BaseMessage
import operator

# from ..models.resume import Resume

class EireGateState(TypedDict):
    raw_text: str
    parsed_resume: Dict
    target_role: str
    target_company: str
    tailored_resume: Dict
    match_score: float
    visa_advice: str
    messages: Annotated[List[BaseMessage], operator.add]
