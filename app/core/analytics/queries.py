from sqlalchemy import func
from app.database.models import (
    Session as DBSession,
    Prompt,
    ExecutionPlan,
    ExecutionStep,
    ExecutionResult,
    Retry
)


def get_session_summary(db):
    total_sessions = db.query(func.count(DBSession.id)).scalar()
    total_steps = db.query(func.count(ExecutionStep.id)).scalar()
    total_results = db.query(func.count(ExecutionResult.id)).scalar()
    total_retries = db.query(func.count(Retry.id)).scalar()

    return {
        "sessions": total_sessions or 0,
        "steps": total_steps or 0,
        "results": total_results or 0,
        "retries": total_retries or 0
    }


def get_recent_sessions(db, limit=5):
    return (
        db.query(DBSession)
        .order_by(DBSession.id.desc())
        .limit(limit)
        .all()
    )


def get_recent_prompts(db, limit=5):
    return (
        db.query(Prompt)
        .order_by(Prompt.id.desc())
        .limit(limit)
        .all()
    )


def get_failed_steps(db):
    return (
        db.query(ExecutionResult)
        .filter(ExecutionResult.return_code != 0)
        .all()
    )


def get_retry_stats(db):
    return db.query(Retry).all()
