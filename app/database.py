from sqlalchemy import create_engine, Column, Integer, String, Text, text
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine(
    "sqlite:///users.db",
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


class Session(Base):

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)

    user_id = Column(String, unique=True)

    step = Column(String, default="start")

    dob = Column(String)

    tob = Column(String)

    place = Column(String)

    language = Column(String)

    script = Column(String)

    last_domain = Column(String)

    chart_data = Column(Text)


def _ensure_schema_updates():
    """Apply lightweight SQLite schema updates for existing local databases."""
    with engine.begin() as conn:
        columns = {
            row[1]
            for row in conn.execute(text("PRAGMA table_info(sessions)"))
        }

        if columns and "script" not in columns:
            conn.execute(text("ALTER TABLE sessions ADD COLUMN script VARCHAR"))


Base.metadata.create_all(engine)
_ensure_schema_updates()