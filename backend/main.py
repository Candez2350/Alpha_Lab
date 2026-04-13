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

import threading
from core.db import SessionLocal, RankAlphaSelection
from core.cron_jobs import run_all_jobs

# Initialize DB
@app.on_event("startup")
def on_startup():
    init_db()
    db = SessionLocal()
    try:
        count = db.query(RankAlphaSelection).count()
        if count == 0:
            print("First run detected. Generating initial rankings in background...")
            threading.Thread(target=run_all_jobs).start()
    except Exception as e:
        print(f"Error checking DB: {e}")
    finally:
        db.close()

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

@app.post("/api/system/cron", tags=["System"])
async def run_daily_cron(api_key: str = Depends(get_api_key)):
    """
    Gatilho da rotina diária (23:30). Roda todos os motores e atualiza os rankings no banco de dados.
    """
    try:
        from core.cron_jobs import run_all_jobs
        import threading
        threading.Thread(target=run_all_jobs).start()
        return {"status": "success", "message": "Cron jobs started in background."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao iniciar cron jobs: {str(e)}")

# --- 1. MÓDULO DE SELEÇÃO E ALPHA (STOCK PICKING) ---


@app.get("/api/selection/magic-momentum", tags=["Seleção"])
async def get_alpha_picks(
    n_mf: int = 6, 
    n_bancos: int = 2, 
    n_eletricas: int = 2,
    db: Session = Depends(get_db)
):
    """
    Retorna seleção de ativos baseada em Magic Formula e Momentum de Bancos/Elétricas (via DB).
    """
    try:
        from core.db import RankAlphaSelection
        from sqlalchemy import select
        
        # Magic Formula
        mf_query = select(RankAlphaSelection).where(RankAlphaSelection.setor == 'MF').order_by(RankAlphaSelection.rank_final.asc()).limit(n_mf)
        mf_results = db.execute(mf_query).scalars().all()
        
        # Momentum Bancos
        bancos_query = select(RankAlphaSelection).where(RankAlphaSelection.setor == 'BANCO').order_by(RankAlphaSelection.momentum.desc()).limit(n_bancos)
        bancos_results = db.execute(bancos_query).scalars().all()
        
        # Momentum Eletricas
        eletricas_query = select(RankAlphaSelection).where(RankAlphaSelection.setor == 'ELETRICA').order_by(RankAlphaSelection.momentum.desc()).limit(n_eletricas)
        eletricas_results = db.execute(eletricas_query).scalars().all()
        
        from datetime import datetime
        return {
            "magic_formula": [{"ticker": r.ticker, "evebit": r.evebit, "roic": r.roic, "magic_score": r.rank_final} for r in mf_results],
            "momentum": [{"ticker": r.ticker, "setor": r.setor, "score": r.momentum} for r in bancos_results + eletricas_results],
            "updated_at": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no Motor de Seleção: {str(e)}")

@app.get("/api/selection/monthly-portfolio", tags=["Seleção"])
async def get_monthly_allocation(
    capital: float = Query(10000.0, description="Capital total disponível (R$)"),
    n_br: int = Query(5, description="Número de ativos BR"),
    n_bdr: int = Query(5, description="Número de ativos BDR (Internacional)"),
    db: Session = Depends(get_db)
):
    """
    Gera carteira mensal otimizada com lógica de 'Caixa Zerado' e pesos percentuais.
    """
    try:
        from core.db import RankMonthlyAllocation
        from sqlalchemy import select
        import pandas as pd
        from core.engine_monthly_bdr import MonthlyBdrEngine
        
        # BR
        br_query = select(RankMonthlyAllocation).where(RankMonthlyAllocation.tipo_ativo == 'BR').order_by(RankMonthlyAllocation.peso_sugerido.asc()).limit(n_br)
        br_results = db.execute(br_query).scalars().all()
        
        # BDR
        bdr_query = select(RankMonthlyAllocation).where(RankMonthlyAllocation.tipo_ativo == 'BDR').order_by(RankMonthlyAllocation.peso_sugerido.asc()).limit(n_bdr)
        bdr_results = db.execute(bdr_query).scalars().all()
        
        all_results = br_results + bdr_results
        if not all_results:
            return {}
            
        # Reconstruct portfolio dataframe for optimize_allocation
        portfolio_data = []
        for r in all_results:
            portfolio_data.append({
                'ticker': r.ticker,
                'tipo': "AÇÃO BR" if r.tipo_ativo == 'BR' else "BDR USA",
                'preco': r.preco,
                'tendencia': r.tendencia
            })
            
        df_portfolio = pd.DataFrame(portfolio_data)
        
        engine = MonthlyBdrEngine()
        return engine.optimize_allocation(df_portfolio, capital)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na Otimização de Alocação: {str(e)}")

# --- 2. MÓDULO DE ARBITRAGEM (ESTATÍSTICA) ---

@app.get("/api/strategy/long-short/scan", tags=["Arbitragem"])
async def get_ls_scan(
    capital: float = Query(20000.0, description="Capital para exposição do par"),
    tickers: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Lê os pares da tabela rank_long_short e calcula a boleta de execução.
    """
    try:
        from core.db import RankLongShort
        from sqlalchemy import select
        
        # Filtra opcionalmente os tickers se fornecidos
        query = select(RankLongShort).order_by(RankLongShort.zscore.desc())
        results = db.execute(query).scalars().all()
        
        opportunities = []
        for r in results:
            if tickers:
                parts = r.par.split(' x ')
                if parts[0] not in tickers and parts[1] not in tickers:
                    continue
                    
            ativo_y, ativo_x = r.par.split(' x ')
            p_long, p_short = r.preco_x, r.preco_y # As gravadas no banco
            
            # Recalcula a boleta (Mesma lógica de engine_ls.scan_opportunities mas direto com preço/ratio)
            z = r.zscore
            if z < 0:
                long, short = ativo_y, ativo_x
            else:
                long, short = ativo_x, ativo_y
                
            ratio = r.ratio
            
            # Cálculo da Alocação (Financeiro)
            financeiro_ponta = capital / 2 # Exposição dividida
            qtd_long = round(financeiro_ponta / p_long, -2) if p_long > 0 else 0
            if qtd_long == 0 and p_long > 0: qtd_long = 100
            
            financeiro_real_long = qtd_long * p_long
            qtd_short = round((financeiro_real_long * ratio) / p_short, -2) if p_short > 0 else 0
            if qtd_short == 0 and p_short > 0: qtd_short = 100
            
            financeiro_real_short = qtd_short * p_short

            import json
            hist_z = []
            try:
                hist_z = json.loads(r.status_cointegracao) if r.status_cointegracao.startswith('[') else r.status_cointegracao
            except:
                pass

            opportunities.append({
                "par": r.par,
                "z_score": round(z, 2),
                "history_z_score": hist_z if isinstance(hist_z, list) else [],
                "half_life": round(r.half_life, 1),
                "robustez": r.status_cointegracao if not r.status_cointegracao.startswith('[') else '',
                "boleta": {
                    "long": {"ticker": long, "qtd": int(qtd_long), "financeiro": round(financeiro_real_long, 2)},
                    "short": {"ticker": short, "qtd": int(qtd_short), "financeiro": round(financeiro_real_short, 2)},
                    "financeiro_total": round(financeiro_real_long + financeiro_real_short, 2),
                    "composicao_pct": {
                        long: round((financeiro_real_long / (financeiro_real_long + financeiro_real_short)) * 100, 1) if financeiro_real_long > 0 else 0,
                        short: round((financeiro_real_short / (financeiro_real_long + financeiro_real_short)) * 100, 1) if financeiro_real_short > 0 else 0
                    }
                }
            })
            
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
async def get_volatility_analysis(ticker: str, db: Session = Depends(get_db)):
    """
    Radar de Volatilidade: Lê da tabela pré-calculada rank_options_analysis.
    """
    try:
        from core.db import RankOptionsAnalysis
        from sqlalchemy import select
        
        ticker_clean = ticker.replace('.SA', '')
        query = select(RankOptionsAnalysis).where(RankOptionsAnalysis.ticker == ticker_clean)
        result = db.execute(query).scalars().first()
        
        if not result:
            raise ValueError("Ativo não encontrado ou sem análise disponível.")
            
        analysis = {
            "hv20": result.hv20,
            "hv50": result.hv50,
            "vol_status": result.vol_status,
            "squeeze_on": result.squeeze_on,
            "direction": result.direction,
            "qullamaggie": {
                "breakout": {"status": result.qullamaggie_status},
                "episodic_pivot": {"active": result.is_ep},
                "parabolic_short": {"active": result.is_parabolic},
                "momentum_60d": result.momentum_60d
            }
        }
        
        return {"ticker": ticker, "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/options/scan", tags=["Opções"])
async def get_options_scan(db: Session = Depends(get_db)):
    """
    Varre o IBRX-100 buscando ativos com Squeeze ativado ou setups Qullamaggie formando/ativados (via DB).
    """
    try:
        from core.db import RankOptionsAnalysis
        from sqlalchemy import select
        
        # Filtra apenas os que têm algo interessante
        query = select(RankOptionsAnalysis).where(
            (RankOptionsAnalysis.squeeze_on == True) | 
            (RankOptionsAnalysis.qullamaggie_status.in_(['🔥 BREAKOUT', '💤 SETUP FORMANDO'])) |
            (RankOptionsAnalysis.is_ep == True) |
            (RankOptionsAnalysis.is_parabolic == True)
        ).order_by(RankOptionsAnalysis.momentum_60d.desc())
        
        results = db.execute(query).scalars().all()
        
        formatted_results = []
        for r in results:
            formatted_results.append({
                "ticker": r.ticker,
                "squeeze": r.squeeze_on,
                "qullamaggie_status": r.qullamaggie_status,
                "is_ep": r.is_ep,
                "is_parabolic": r.is_parabolic,
                "direction": r.direction,
                "momentum_60d": r.momentum_60d
            })
            
        return {"status": "success", "count": len(formatted_results), "data": formatted_results}
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