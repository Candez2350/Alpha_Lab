import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Boolean
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

class RankAlphaSelection(Base):
    __tablename__ = "rank_alpha_selection"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)
    roic = Column(Float)
    evebit = Column(Float)
    momentum = Column(Float)
    setor = Column(String)
    rank_final = Column(Integer)

class RankLongShort(Base):
    __tablename__ = "rank_long_short"
    
    id = Column(Integer, primary_key=True, index=True)
    par = Column(String, index=True)
    zscore = Column(Float)
    half_life = Column(Float)
    adf_pvalue = Column(Float)
    status_cointegracao = Column(String)
    rentabilidade_estimada = Column(Float)
    preco_x = Column(Float)
    preco_y = Column(Float)
    ratio = Column(Float)

class RankOptionsAnalysis(Base):
    __tablename__ = "rank_options_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)
    hv20 = Column(Float)
    hv50 = Column(Float)
    vol_status = Column(String)
    squeeze_on = Column(Boolean)
    direction = Column(String)
    qullamaggie_status = Column(String)
    momentum_60d = Column(Float)
    is_ep = Column(Boolean)
    is_parabolic = Column(Boolean)

class RankMonthlyAllocation(Base):
    __tablename__ = "rank_monthly_allocation"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)
    peso_sugerido = Column(Float)
    tipo_ativo = Column(String)
    preco = Column(Float)
    tendencia = Column(String)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
