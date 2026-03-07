from app.database import SessionLocal, Session


class StateManager:

    @staticmethod
    def get_session(user_id: str):

        db = SessionLocal()

        session = db.query(Session).filter(Session.user_id == user_id).first()

        if not session:
            session = Session(
                user_id=user_id,
                step="start",
                last_domain=None,
                language="en",
                chart_data=None
            )
            db.add(session)
            db.commit()

        db.close()
        return session

    @staticmethod
    def update_session(user_id: str, **kwargs):

        db = SessionLocal()

        session = db.query(Session).filter(Session.user_id == user_id).first()

        if not session:
            db.close()
            return

        for key, value in kwargs.items():
            setattr(session, key, value)

        db.commit()
        db.close()

    @staticmethod
    def reset(user_id: str):

        db = SessionLocal()

        session = db.query(Session).filter(Session.user_id == user_id).first()

        if session:
            session.step = "start"
            session.last_domain = None

        db.commit()
        db.close()