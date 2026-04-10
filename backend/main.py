from fastapi import FastAPI, HTTPException, Query, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn
import os

# Motores Core do Sistema
from core.engine_ls import LongShortEngine
from core.engine_opt import OptionsEngine
from core.engine_selection import SelectionEngine
from core.engine_monthly_bdr import MonthlyBdrEngine
from core.constants import VIP_TICKERS, IBRX_100
from core.db import init_db, get_db
from sqlalchemy.orm import Session
from core.sync_etl import run_sync_pipeline

app = FastAPI(
    title="Candez Quant Platform API",
    description="Terminal de Inteligência Quantitativa: Arbitragem, Opções e Alocação Tática",
    version="1.1.0"
)

# Initialize DB
@app.on_event("startup")
def on_startup():
    init_db()

# --- CONFIGURAÇÃO DE CORS ---
# Permite que o Front-end (Vercel) consuma os dados do Back-end (Railway/Render)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

def get_api_key(api_key_header: str = Security(api_key_header)):
    expected_key = os.getenv("SYNC_SECRET_KEY", "default_secret_for_local_dev")
    if api_key_header == expected_key:
        return api_key_header
    raise HTTPException(status_code=403, detail="Could not validate credentials")

@app.post("/api/system/sync", tags=["System"])
async def sync_database(api_key: str = Depends(get_api_key), db: Session = Depends(get_db)):
    """
    Sincroniza os dados de mercado e fundamentos para o banco de dados.
    """
    try:
        return run_sync_pipeline(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no pipeline de sincronização: {str(e)}")

# --- 1. MÓDULO DE SELEÇÃO E ALPHA (STOCK PICKING) ---


@app.get("/api/selection/magic-momentum", tags=["Seleção"])
async def get_alpha_picks(
    n_mf: int = 6, 
    n_bancos: int = 2, 
    n_eletricas: int = 2
):
    """
    Retorna seleção de ativos baseada em Magic Formula e Momentum de Bancos/Elétricas.
    """
    try:
        engine = SelectionEngine()
        return engine.get_final_selection(n_mf=n_mf, n_bancos=n_bancos, n_eletricas=n_eletricas)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no Motor de Seleção: {str(e)}")

@app.get("/api/selection/monthly-portfolio", tags=["Seleção"])
async def get_monthly_allocation(
    capital: float = Query(10000.0, description="Capital total disponível (R$)"),
    n_br: int = Query(5, description="Número de ativos BR"),
    n_bdr: int = Query(5, description="Número de ativos BDR (Internacional)")
):
    """
    Gera carteira mensal otimizada com lógica de 'Caixa Zerado' e pesos percentuais.
    """
    try:
        engine = MonthlyBdrEngine()
        # Gera a carteira dinâmica baseada no aporte do usuário
        result = engine.get_monthly_portfolio(capital=capital, n_ativos_br=n_br, n_ativos_bdr=n_bdr)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na Otimização de Alocação: {str(e)}")

# --- 2. MÓDULO DE ARBITRAGEM (ESTATÍSTICA) ---

@app.get("/api/strategy/long-short/scan", tags=["Arbitragem"])
async def get_ls_scan(
    capital: float = Query(20000.0, description="Capital para exposição do par"),
    tickers: Optional[List[str]] = Query(None)
):
    """
    Varre o mercado em busca de pares cointegrados (ADF) e calcula a boleta de execução.
    """
    try:
        target_list = tickers if tickers else IBRX_100
        engine = LongShortEngine()
        df_prices = engine.get_market_data(target_list)
        opportunities = engine.scan_opportunities(df_prices, capital_total=capital)
        return {"status": "success", "count": len(opportunities), "data": opportunities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no Scanner L&S: {str(e)}")

# --- 3. MÓDULO DE DERIVATIVOS E VOLATILIDADE ---

@app.get("/api/options/calculator", tags=["Opções"])
async def get_options_pricing(
    s: float, k: float, t_days: int, r: float = 0.1175, sigma: float = 0.30, tipo: str = 'call'
):
    """
    Calculadora Black-Scholes: Preço Justo e Gregas (Delta, Gamma, Theta, Vega).
    """
    try:
        t_years = t_days / 252
        return OptionsEngine.black_scholes(S=s, K=k, T=t_years, r=r, sigma=sigma, option_type=tipo)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Erro no cálculo de precificação")

@app.get("/api/options/vol-radar", tags=["Opções"])
async def get_volatility_analysis(ticker: str):
    """
    Radar de Volatilidade: Detecta Squeeze (Bollinger/Keltner) e status da Vol Histórica.
    """
    try:
        from core.db import engine
        import pandas as pd
        engine_opt = OptionsEngine()
        
        ticker_sa = f"{ticker}.SA"
        query = select(
            DailyPrice.date, DailyPrice.ticker, DailyPrice.close, 
            DailyPrice.high, DailyPrice.low, DailyPrice.open, DailyPrice.volume
        ).where(DailyPrice.ticker == ticker_sa).order_by(DailyPrice.date.asc())
        
        df_ativo = pd.read_sql(query, engine)
        
        if df_ativo.empty:
            raise ValueError("Ativo não encontrado ou sem histórico no banco de dados")
            
        df_ativo.set_index('date', inplace=True)
        df_ativo.index = pd.to_datetime(df_ativo.index)
        df_ativo.rename(columns={'close': 'Close', 'high': 'High', 'low': 'Low', 'open': 'Open', 'volume': 'Volume'}, inplace=True)
        
        analysis = engine_opt.analyze_volatility_and_squeeze(df_ativo)
        return {"ticker": ticker, "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/options/scan", tags=["Opções"])
async def get_options_scan():
    """
    Varre o IBRX-100 buscando ativos com Squeeze ativado ou setups Qullamaggie formando/ativados.
    """
    try:
        from core.db import engine
        import pandas as pd
        engine_opt = OptionsEngine()
        
        # Get IBRX 100 tickers from DB
        query = "SELECT ticker FROM ibrx_100"
        df_ibrx = pd.read_sql(query, engine)
        tickers = [t.replace('.SA', '') for t in df_ibrx['ticker'].tolist()]
        
        if not tickers:
            tickers = IBRX_100 # Fallback
            
        results = engine_opt.scan_market(tickers)
        return {"status": "success", "count": len(results), "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no Scanner de Opções: {str(e)}")

# --- STATUS ---
@app.get("/", tags=["Status"])
async def system_status():
    return {
        "status": "online",
        "platform": "Candez Quant Platform",
        "owner": "Roger Fellipe Candez Ramos Serra",
        "version": "1.1.0"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)