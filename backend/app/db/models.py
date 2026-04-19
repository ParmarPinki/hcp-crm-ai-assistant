from sqlalchemy import JSON, Column, Date, DateTime, Integer, String, Text, func

from app.db.database import Base


class Interaction(Base):
    __tablename__ = 'interactions'

    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String(255), nullable=True)
    interaction_type = Column(String(100), nullable=True)
    interaction_date = Column(Date, nullable=True)
    interaction_time = Column(String(50), nullable=True)
    attendees = Column(Text, nullable=True)
    topics_discussed = Column(Text, nullable=True)
    sentiment = Column(String(50), nullable=True)
    materials_shared = Column(JSON, nullable=True)
    samples_distributed = Column(JSON, nullable=True)
    outcomes = Column(Text, nullable=True)
    follow_up_actions = Column(Text, nullable=True)
    suggestions = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AIAuditLog(Base):
    __tablename__ = 'ai_audit_logs'

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    tool_used = Column(String(100), nullable=False)
    user_message = Column(Text, nullable=False)
    assistant_message = Column(Text, nullable=False)
    form_patch = Column(JSON, nullable=True)
    suggestions = Column(JSON, nullable=True)
    model_name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
