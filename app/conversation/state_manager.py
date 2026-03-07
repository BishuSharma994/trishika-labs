from app.database import SessionLocal, Session


class StateManager:

    @staticmethod
    def update_session(user_id, **fields):

        db = SessionLocal()

        session = db.query(Session).filter(Session.user_id == user_id).first()

        if not session:
            session = Session(user_id=user_id)
            db.add(session)

        for key, value in fields.items():
            setattr(session, key, value)

        db.commit()
        db.close()