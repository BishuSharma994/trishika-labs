from types import SimpleNamespace

from app.database import Session, SessionLocal


class StateManager:
    SESSION_FIELDS = tuple(column.name for column in Session.__table__.columns)
    SESSION_FIELDS_SET = set(SESSION_FIELDS)

    @staticmethod
    def _snapshot(session):
        if not session:
            return None

        data = {field: getattr(session, field) for field in StateManager.SESSION_FIELDS}
        return SimpleNamespace(**data)

    @staticmethod
    def get_or_create_session(user_id):
        db = SessionLocal()
        try:
            session = db.query(Session).filter(Session.user_id == user_id).first()

            if not session:
                session = Session(user_id=user_id, step="start")
                db.add(session)
                db.flush()

            db.commit()
            db.refresh(session)
            return StateManager._snapshot(session)
        finally:
            db.close()

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
    def update_session(user_id, **fields):
        db = SessionLocal()
        try:
            session = db.query(Session).filter(Session.user_id == user_id).first()

            if not session:
                session = Session(user_id=user_id, step="start")
                db.add(session)
                db.flush()

            for key, value in fields.items():
                if key in StateManager.SESSION_FIELDS_SET:
                    setattr(session, key, value)

            db.commit()
            db.refresh(session)
            return StateManager._snapshot(session)
        finally:
            db.close()
