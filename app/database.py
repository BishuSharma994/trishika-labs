# app/database.py

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

# =============================
# ENGINE
# =============================

engine = create_engine(
    "sqlite:///users.db",
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# =============================
# SESSION TABLE
# =============================

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)

    # Conversation state
    step = Column(String, default="start")

    # Birth details
    dob = Column(String, nullable=True)
    tob = Column(String, nullable=True)
    place = Column(String, nullable=True)

    # === NEW FIELDS ===
    # Cached deterministic chart
    chart_data = Column(Text, nullable=True)

    # Remember last asked domain
    last_domain = Column(String, nullable=True)

    # Conversation continuity flag
    conversation_mode = Column(Boolean, default=True)


# =============================
# CREATE TABLES
# =============================

Base.metadata.create_all(engine)