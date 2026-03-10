from types import SimpleNamespace

from app.database import SessionLocal, Session


class StateManager:

    SESSION_FIELDS = tuple(column.name for column in Session.__table__.columns)
    SESSION_FIELDS_SET = set(SESSION_FIELDS)

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
    def get_or_create_session(user_id):
        db = SessionLocal()
        try:
            session = db.query(Session).filter(Session.user_id == user_id).first()

        try:
            session = db.query(Session).filter(Session.user_id == user_id).first()

            if not session:
                session = Session(user_id=user_id, step="start")
                db.add(session)
                db.commit()

            db.refresh(session)
            return session
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
                setattr(session, key, value)

            db.commit()
            db.refresh(session)

            return {
                "user_id": session.user_id,
                "step": session.step,
                "language": session.language,
                "script": session.script
            }
        finally:
            db.close()
