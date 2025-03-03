from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./fire_detections.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class FireDetection(Base):
    __tablename__ = "fire_detections"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp_start = Column(DateTime, nullable=False)
    timestamp_end = Column(DateTime, nullable=False)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database initialized.")