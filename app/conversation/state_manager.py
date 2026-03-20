import json
from types import SimpleNamespace
from app.database import SessionLocal, Session


class StateManager:

    SESSION_FIELDS     = tuple(column.name for column in Session.__table__.columns)
    SESSION_FIELDS_SET = set(SESSION_FIELDS)
    JSON_TEXT_FIELDS   = {"language_state_blob", "consultation_state_blob", "profiles", "chart_data"}

    @staticmethod
    def _snapshot(session):
        if not session:
            return None
        data = {
            field: getattr(session, field)
            for field in StateManager.SESSION_FIELDS
        }
        return SimpleNamespace(**data)

    @staticmethod
    def get_session(user_id):
        db = SessionLocal()
        try:
            session = db.query(Session).filter(Session.user_id == user_id).first()
            return StateManager._snapshot(session)
        finally:
            db.close()

    @staticmethod
    def reload_session(user_id):
        return StateManager.get_session(user_id)

    @staticmethod
    def _normalize_field_value(key, value):
        if key not in StateManager.JSON_TEXT_FIELDS or value is None or isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False, default=str)

    @staticmethod
    def get_or_create_session(user_id):
        db = SessionLocal()
        try:
            session = db.query(Session).filter(Session.user_id == user_id).first()
            if not session:
                session = Session(user_id=user_id, step="start")
                db.add(session)
                db.commit()
                db.refresh(session)
            return StateManager._snapshot(session)   # ← FIX: was returning raw ORM object
        finally:
            db.close()

    @staticmethod
    def update_session(user_id, **fields):
        db = SessionLocal()
        try:
            session = db.query(Session).filter(Session.user_id == user_id).first()
            if not session:
                session = Session(user_id=user_id, step="start")
                db.add(session)
            for key, value in fields.items():
                if key in StateManager.SESSION_FIELDS_SET:   # ← FIX: only set valid columns
                    setattr(session, key, StateManager._normalize_field_value(key, value))
            db.commit()
            db.refresh(session)
            return {
                "user_id":  session.user_id,
                "step":     session.step,
                "language": session.language,
                "script":   session.script,
            }
        finally:
            db.close()
