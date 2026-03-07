from sqlalchemy import create_engine, Column, Integer, String, Text
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

    last_domain = Column(String)

    chart_data = Column(Text)


Base.metadata.create_all(engine)