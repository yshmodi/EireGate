from typing import TypedDict, Annotated, List, Dict
from langchain_core.messages import BaseMessage
import operator


class EireGateState(TypedDict):
    raw_text: str
    parsed_resume: Dict
    jd_text: str  # Job description from selected job
    target_role: str
    target_company: str
    tailored_resume: Dict
    match_score: float
    messages: Annotated[List[BaseMessage], operator.add]
