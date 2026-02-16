from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    read_count = Column(Integer, default=0)
    write_count = Column(Integer, default=0)
    retry_count = Column(Integer, default=0)
    risk_score = Column(Integer, default=0)

    prompts = relationship("Prompt", back_populates="session")


class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("Session", back_populates="prompts")
    execution_plan = relationship("ExecutionPlan", back_populates="prompt", uselist=False)


class ExecutionPlan(Base):
    __tablename__ = "execution_plans"

    id = Column(Integer, primary_key=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id"))
    plan_json = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    prompt = relationship("Prompt", back_populates="execution_plan")
    steps = relationship("ExecutionStep", back_populates="plan")


class ExecutionStep(Base):
    __tablename__ = "execution_steps"

    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey("execution_plans.id"))
    step_order = Column(Integer, nullable=False)
    tool = Column(String, nullable=False)
    action = Column(String, nullable=False)
    command = Column(Text, nullable=True)
    file_path = Column(Text, nullable=True)
    content = Column(Text, nullable=True)

    plan = relationship("ExecutionPlan", back_populates="steps")
    result = relationship("ExecutionResult", back_populates="step", uselist=False)
    retries = relationship("Retry", back_populates="step")


class ExecutionResult(Base):
    __tablename__ = "execution_results"

    id = Column(Integer, primary_key=True)
    step_id = Column(Integer, ForeignKey("execution_steps.id"))
    stdout = Column(Text)
    stderr = Column(Text)
    return_code = Column(Integer)
    executed_at = Column(DateTime(timezone=True), server_default=func.now())

    step = relationship("ExecutionStep", back_populates="result")


class Retry(Base):
    __tablename__ = "retries"

    id = Column(Integer, primary_key=True)
    step_id = Column(Integer, ForeignKey("execution_steps.id"))
    retry_plan = Column(JSONB)
    retry_number = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    step = relationship("ExecutionStep", back_populates="retries")
