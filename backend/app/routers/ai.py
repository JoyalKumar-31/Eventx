from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_optional_current_user
from app.models.user import User
from app.schemas.ai import (
    AIChatRequest,
    AIChatResponse,
    AgentQueryRequest,
    AgentQueryResponse,
    AgentInfoOut
)
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["FEST AI Assistant"])


@router.post("/chat", response_model=AIChatResponse)
def chat_with_fest_ai(
    req: AIChatRequest,
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Context-aware FEST AI Assistant powered by LangGraph multi-agent workflow.
    Understands user intent, queries live MySQL fest database across 7 specialized agents,
    and returns intelligent conversational responses along with structured action cards
    (e.g. VIEW_EVENT, REGISTER_EVENT, VIEW_PASS, VIEW_LEADERBOARD, VIEW_ANALYTICS).
    """
    return AIService.process_message(
        db=db,
        message=req.message,
        user=current_user,
        session_id=req.session_id
    )


@router.post("/agents/query", response_model=AgentQueryResponse)
def query_fest_agent_network(
    req: AgentQueryRequest,
    current_user: User = Depends(get_optional_current_user)
):
    """
    Direct multi-agent network execution endpoint (compatible with teammate's spec).
    Accepts question, user role, and optional event context,
    invokes the LangGraph supervisor workflow, and returns the response,
    the specialized agent route taken, execution trace, and tool outputs.
    """
    effective_role = req.role or (current_user.role.value.lower() if current_user else "student")
    return AIService.execute_agent_workflow(
        question=req.question,
        role=effective_role,
        event_context=req.event_context
    )


@router.get("/agents/info", response_model=List[AgentInfoOut])
def get_agents_directory():
    """
    Returns the full directory of all 7 specialized AI agents deployed in FESTORA,
    including their designated responsibilities, tool bindings, and capabilities.
    """
    return AIService.get_agents_info()
