from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, text
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine(
    "sqlite:///users.db",
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Session(Base):
    __tablename__ = "sessions"

    id                       = Column(Integer, primary_key=True)
    user_id                  = Column(String, unique=True)
    step                     = Column(String, default="start")
    dob                      = Column(String)
    tob                      = Column(String)
    place                    = Column(String)
    language                 = Column(String)
    script                   = Column(String)
    language_mode            = Column(String)
    language_confirmed       = Column(Boolean, default=False)
    language_state_blob      = Column(Text)          # ← ADDED
    consultation_state_blob  = Column(Text)          # ← ADDED
    last_domain              = Column(String)
    conversation_phase       = Column(String)
    last_followup_question   = Column(Text)
    persona_introduced       = Column(Boolean, default=False)
    age                      = Column(Integer)
    life_stage               = Column(String)
    user_goal                = Column(String)
    plan_tier                = Column(String, default="free")
    profiles                 = Column(Text)
    pending_profile_name     = Column(String)
    active_profile_name      = Column(String)
    chart_data               = Column(Text)
    theme_shown              = Column(Boolean, default=False)


def _ensure_schema_updates():
    """Apply lightweight SQLite schema updates for existing local databases."""
    with engine.begin() as conn:
        columns = {
            row[1] for row in conn.execute(text("PRAGMA table_info(sessions)"))
        }
        if not columns:
            return

        migrations = [
            ("script",                   "ALTER TABLE sessions ADD COLUMN script VARCHAR"),
            ("theme_shown",              "ALTER TABLE sessions ADD COLUMN theme_shown BOOLEAN DEFAULT 0"),
            ("conversation_phase",       "ALTER TABLE sessions ADD COLUMN conversation_phase VARCHAR"),
            ("last_followup_question",   "ALTER TABLE sessions ADD COLUMN last_followup_question TEXT"),
            ("persona_introduced",       "ALTER TABLE sessions ADD COLUMN persona_introduced BOOLEAN DEFAULT 0"),
            ("age",                      "ALTER TABLE sessions ADD COLUMN age INTEGER"),
            ("life_stage",               "ALTER TABLE sessions ADD COLUMN life_stage VARCHAR"),
            ("user_goal",                "ALTER TABLE sessions ADD COLUMN user_goal VARCHAR"),
            ("plan_tier",                "ALTER TABLE sessions ADD COLUMN plan_tier VARCHAR DEFAULT 'free'"),
            ("profiles",                 "ALTER TABLE sessions ADD COLUMN profiles TEXT"),
            ("pending_profile_name",     "ALTER TABLE sessions ADD COLUMN pending_profile_name VARCHAR"),
            ("active_profile_name",      "ALTER TABLE sessions ADD COLUMN active_profile_name VARCHAR"),
            ("language_mode",            "ALTER TABLE sessions ADD COLUMN language_mode VARCHAR"),
            ("language_confirmed",       "ALTER TABLE sessions ADD COLUMN language_confirmed BOOLEAN DEFAULT 0"),
            ("language_state_blob",      "ALTER TABLE sessions ADD COLUMN language_state_blob TEXT"),      # ← ADDED
            ("consultation_state_blob",  "ALTER TABLE sessions ADD COLUMN consultation_state_blob TEXT"),  # ← ADDED
        ]

        for col_name, sql in migrations:
            if col_name not in columns:
                conn.execute(text(sql))


Base.metadata.create_all(engine)
_ensure_schema_updates()
