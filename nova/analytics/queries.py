from sqlalchemy import func
from sqlalchemy.exc import ProgrammingError

from nova.database.models import ExecutionResult, ExecutionStep, Prompt, Retry
from nova.database.models import Session as DBSession


def get_session_summary(db):
    try:
        total_sessions = db.query(func.count(DBSession.id)).scalar()
        total_steps = db.query(func.count(ExecutionStep.id)).scalar()
        total_results = db.query(func.count(ExecutionResult.id)).scalar()
        total_retries = db.query(func.count(Retry.id)).scalar()

        return {
            "sessions": total_sessions or 0,
            "steps": total_steps or 0,
            "results": total_results or 0,
            "retries": total_retries or 0,
        }
    except ProgrammingError:
        # Tables don't exist yet, return zeros
        return {
            "sessions": 0,
            "steps": 0,
            "results": 0,
            "retries": 0,
        }


def get_recent_sessions(db, limit=5):
    try:
        return db.query(DBSession).order_by(DBSession.id.desc()).limit(limit).all()
    except ProgrammingError:
        return []


def get_recent_prompts(db, limit=5):
    try:
        return db.query(Prompt).order_by(Prompt.id.desc()).limit(limit).all()
    except ProgrammingError:
        return []


def get_failed_steps(db):
    try:
        return db.query(ExecutionResult).filter(ExecutionResult.return_code != 0).all()
    except ProgrammingError:
        return []


def get_retry_stats(db):
    try:
        return db.query(Retry).all()
    except ProgrammingError:
        return []
