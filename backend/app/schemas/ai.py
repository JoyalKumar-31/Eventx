from typing import Any, List, Optional
from pydantic import BaseModel


class AIActionOut(BaseModel):
    type: str  # VIEW_EVENT, REGISTER_EVENT, VIEW_SCHEDULE, VIEW_PASS, VIEW_LEADERBOARD
    label: str
    event_id: Optional[int] = None
    url: Optional[str] = None


class AIChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class AIChatResponse(BaseModel):
    message: str
    type: str = "text"  # text, event_list, schedule_list, action_card, registration_info
    data: Optional[Any] = None
    actions: List[AIActionOut] = []
    session_id: str


class AIChatMessageOut(BaseModel):
    id: int
    sender: str
    content: str
    message_type: str
    structured_data: Optional[Any] = None
    created_at: str


class AgentQueryRequest(BaseModel):
    question: str
    role: Optional[str] = "student"
    event_context: Optional[dict] = None


class AgentQueryResponse(BaseModel):
    response: str
    route_taken: str
    trace: List[str] = []
    tool_outputs: Optional[dict] = None


class AgentInfoOut(BaseModel):
    name: str
    agent_id: str
    role_title: str
    description: str
    capabilities: List[str]
