from datetime import date
from app.database import SessionLocal, User

def can_use(user_id):
    db = SessionLocal()
    user = db.query(User).filter(User.user_id == str(user_id)).first()
    today = date.today()

    if not user:
        user = User(user_id=str(user_id), count=0, last_reset=today)
        db.add(user)
        db.commit()
        return True

    if user.last_reset != today:
        user.count = 0
        user.last_reset = today
        db.commit()
        return True

    return user.count < 3


def increment_usage(user_id):
    db = SessionLocal()
    user = db.query(User).filter(User.user_id == str(user_id)).first()
    user.count += 1
    db.commit()