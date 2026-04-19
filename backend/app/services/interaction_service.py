from datetime import datetime
from typing import Any, Dict

from sqlalchemy.orm import Session

from app.db.models import AIAuditLog, Interaction


def upsert_interaction(db: Session, payload: Dict[str, Any]) -> Interaction:
    interaction = None
    interaction_id = payload.get('id')
    if interaction_id:
        interaction = db.get(Interaction, interaction_id)

    if interaction is None:
        interaction = Interaction()
        db.add(interaction)

    interaction.hcp_name = payload.get('hcp_name')
    interaction.interaction_type = payload.get('interaction_type')
    interaction.interaction_date = _parse_date(payload.get('interaction_date'))
    interaction.interaction_time = payload.get('interaction_time')
    interaction.attendees = payload.get('attendees')
    interaction.topics_discussed = payload.get('topics_discussed')
    interaction.sentiment = payload.get('sentiment')
    interaction.materials_shared = payload.get('materials_shared') or []
    interaction.samples_distributed = payload.get('samples_distributed') or []
    interaction.outcomes = payload.get('outcomes')
    interaction.follow_up_actions = payload.get('follow_up_actions')
    interaction.suggestions = payload.get('suggestions') or []

    db.commit()
    db.refresh(interaction)
    return interaction


def create_audit_log(db: Session, session_id: str, tool_used: str, user_message: str, assistant_message: str, form_patch: Dict[str, Any], suggestions: list[str], model_name: str) -> None:
    audit = AIAuditLog(
        session_id=session_id,
        tool_used=tool_used,
        user_message=user_message,
        assistant_message=assistant_message,
        form_patch=form_patch,
        suggestions=suggestions,
        model_name=model_name
    )
    db.add(audit)
    db.commit()


def serialize_interaction(interaction: Interaction) -> Dict[str, Any]:
    return {
        'id': interaction.id,
        'hcp_name': interaction.hcp_name,
        'interaction_type': interaction.interaction_type,
        'interaction_date': interaction.interaction_date.isoformat() if interaction.interaction_date else None,
        'interaction_time': interaction.interaction_time,
        'attendees': interaction.attendees,
        'topics_discussed': interaction.topics_discussed,
        'sentiment': interaction.sentiment,
        'materials_shared': interaction.materials_shared or [],
        'samples_distributed': interaction.samples_distributed or [],
        'outcomes': interaction.outcomes,
        'follow_up_actions': interaction.follow_up_actions,
        'suggestions': interaction.suggestions or [],
        'saved_at': (interaction.updated_at or interaction.created_at or datetime.utcnow()).isoformat()
    }


def _parse_date(value: str | None):
    if not value:
        return None
    return datetime.strptime(value, '%Y-%m-%d').date()
