from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Float, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry

DATABASE_URL = "postgresql+asyncpg://fire_user:fire_pass@localhost/fire_db"

engine = create_async_engine(DATABASE_URL, future=True, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


class FireDetection(Base):
    __tablename__ = "fire_detections"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)
    geom = Column(Geometry("POINT", srid=4326), nullable=False)
