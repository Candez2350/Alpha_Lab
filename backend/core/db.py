import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
# To allow local execution without DB strictly defined for now, fallback to sqlite for testing
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./backend_db.sqlite"

# Handle PostgreSQL vs SQLite differences for SQLAlchemy
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DailyPrice(Base):
    __tablename__ = "daily_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)
    date = Column(Date, index=True)
    close = Column(Float)
    high = Column(Float)
    low = Column(Float)
    open = Column(Float)
    volume = Column(Float)

class Fundamental(Base):
    __tablename__ = "fundamentals"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, index=True)
    roic = Column(Float)
    evebit = Column(Float)
    liq2m = Column(Float)
    cotacao = Column(Float)
    setor = Column(String, nullable=True)
    
class BDR(Base):
    __tablename__ = "bdrs"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, index=True)

class IBRX100(Base):
    __tablename__ = "ibrx_100"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, index=True)
    weight = Column(Float, nullable=True)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
