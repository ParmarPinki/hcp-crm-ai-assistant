from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.langgraph_agent import graph_app
from app.core.config import settings
from app.db.database import get_db
from app.db.models import Interaction
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.interaction import InteractionCreate, InteractionResponse
from app.services.interaction_service import create_audit_log, serialize_interaction, upsert_interaction

router = APIRouter(prefix='/api')


@router.post('/ai/chat', response_model=ChatResponse)
async def ai_chat(payload: ChatRequest, db: Session = Depends(get_db)):
    result = graph_app.invoke({
        'session_id': payload.session_id,
        'user_message': payload.message,
        'current_form': payload.current_form,
        'form_patch': {},
        'suggestions': []
    })
    create_audit_log(
        db=db,
        session_id=payload.session_id,
        tool_used=result.get('tool_used', 'log_interaction'),
        user_message=payload.message,
        assistant_message=result.get('assistant_message', 'Done.'),
        form_patch=result.get('form_patch', {}),
        suggestions=result.get('suggestions', []),
        model_name=settings.model_name
    )
    return ChatResponse(
        assistant_message=result.get('assistant_message', 'Done.'),
        tool_used=result.get('tool_used', 'log_interaction'),
        form_patch=result.get('form_patch', {}),
        suggestions=result.get('suggestions', [])
    )


@router.post('/interactions', response_model=InteractionResponse)
def save_interaction(payload: InteractionCreate, db: Session = Depends(get_db)):
    interaction = upsert_interaction(db, payload.model_dump())
    return InteractionResponse(**serialize_interaction(interaction))


@router.get('/interactions/{interaction_id}', response_model=InteractionResponse)
def get_interaction(interaction_id: int, db: Session = Depends(get_db)):
    interaction = db.get(Interaction, interaction_id)
    if interaction is None:
        raise HTTPException(status_code=404, detail='Interaction not found')
    return InteractionResponse(**serialize_interaction(interaction))
