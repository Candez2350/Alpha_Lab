import os
import sys
import json
import logging
from sqlalchemy.orm import Session
from datetime import datetime
import pandas as pd

# Configurar path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db import (
    SessionLocal, init_db, 
    RankAlphaSelection, RankLongShort, RankOptionsAnalysis, RankMonthlyAllocation,
    engine as db_engine, DailyPrice
)
from core.engine_selection import SelectionEngine
from core.engine_ls import LongShortEngine
from core.engine_opt import OptionsEngine
from core.engine_monthly_bdr import MonthlyBdrEngine
from core.constants import IBRX_100

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def update_rank_alpha_selection(db: Session):
    logger.info("Updating Alpha Selection Ranking...")
    engine = SelectionEngine()
    db.query(RankAlphaSelection).delete()
    
    # Busca um universo maior para gravar no banco
    df_mf = engine.get_magic_formula_ranking(top_n=100)
    df_mom = engine.get_momentum_ranking(n_bancos=20, n_eletricas=20)
    
    records = []
    if not df_mf.empty:
        for idx, row in df_mf.iterrows():
            records.append(RankAlphaSelection(
                ticker=row['ticker'],
                roic=row.get('roic', 0),
                evebit=row.get('evebit', 0),
                momentum=0.0,
                setor='MF',
                rank_final=row.get('magic_score', 0)
            ))
            
    if not df_mom.empty:
        for idx, row in df_mom.iterrows():
            records.append(RankAlphaSelection(
                ticker=row['ticker'],
                roic=0.0,
                evebit=0.0,
                momentum=float(row['score']) if 'score' in row else 0.0,
                setor=row.get('setor', ''),
                rank_final=0
            ))
            
    if records:
        db.bulk_save_objects(records)
    logger.info(f"Inserted {len(records)} Alpha Selection records.")

def update_rank_long_short(db: Session):
    logger.info("Updating Long & Short Ranking...")
    engine = LongShortEngine()
    db.query(RankLongShort).delete()
    
    # Varre todo IBRX_100
    df_precos = engine.get_market_data(IBRX_100)
    if not df_precos.empty:
        # Pega as oportunidades sem filtro de capital muito específico, API fará o rateio
        opportunities = engine.scan_opportunities(df_precos, capital_total=20000.0)
        
        records = []
        for opp in opportunities:
            # Reconstruct ratio and prices from boleta
            boleta = opp.get('boleta', {})
            # long and short are dicts with ticker, qtd, financeiro. But wait, I can just recalculate ratio from prices in scan_opportunities, but I didn't save them. Let's just modify the engine to return prices or extract them.
            # Actually we can just use the boleta prices: p_long = financeiro / qtd if qtd != 0
            
            p_long = boleta.get('long', {}).get('financeiro', 0) / boleta.get('long', {}).get('qtd', 1) if boleta.get('long', {}).get('qtd', 0) != 0 else 0
            p_short = boleta.get('short', {}).get('financeiro', 0) / boleta.get('short', {}).get('qtd', 1) if boleta.get('short', {}).get('qtd', 0) != 0 else 0
            
            # Since the API only needs to recalculate with new capital, we can just save ratio = (short_financeiro / long_financeiro) if they were equal weight, but they are weighted by beta.
            # Actually, `scan_opportunities` recalculates the boleta based on `capital_total`. If we just want to recalculate with new capital in the API, we can just re-run `scan_opportunities` for that specific pair? 
            # Or we can just calculate the new quantities proportionally! New_Qtd = Old_Qtd * (New_Capital / Old_Capital). This is mathematically identical and much easier!
            # So I will just save the boleta JSON in rentabilidade_estimada or a new string column? No, I'll just save the JSON in status_cointegracao and parse it later.
            # Let's save history_z_score and boleta as JSON string in status_cointegracao.
            
            import json
            records.append(RankLongShort(
                par=opp['par'],
                zscore=opp.get('z_score', 0.0),
                half_life=opp.get('half_life', 0.0),
                status_cointegracao=opp.get('robustez', ''),
                rentabilidade_estimada=0.0, # Placeholder
                preco_x=p_long,
                preco_y=p_short,
                ratio=1.0 # Placeholder, we will scale by proportion in API
            ))
            
        if records:
            db.bulk_save_objects(records)
        logger.info(f"Inserted {len(records)} Long & Short records.")

def update_rank_options_analysis(db: Session):
    logger.info("Updating Options Analysis Ranking...")
    opt_engine = OptionsEngine()
    db.query(RankOptionsAnalysis).delete()
    
    # Get IBRX 100 tickers from DB
    from sqlalchemy import text
    query = "SELECT ticker FROM ibrx_100"
    df_ibrx = pd.read_sql(query, db_engine)
    tickers = [t.replace('.SA', '') for t in df_ibrx['ticker'].tolist()]
    
    if not tickers:
        tickers = IBRX_100
        
    tickers_sa = [f"{t}.SA" for t in tickers]
    
    query = "SELECT date, ticker, close, high, low, open, volume FROM daily_prices WHERE ticker IN :tickers ORDER BY date ASC"
    # Using straight sql for speed, parameterized
    try:
        from sqlalchemy import select
        q = select(
            DailyPrice.date, DailyPrice.ticker, DailyPrice.close, 
            DailyPrice.high, DailyPrice.low, DailyPrice.open, DailyPrice.volume
        ).where(DailyPrice.ticker.in_(tickers_sa)).order_by(DailyPrice.date.asc())
        
        df_all = pd.read_sql(q, db_engine)
        
        records = []
        if not df_all.empty:
            for t_sa in tickers_sa:
                df_ativo = df_all[df_all['ticker'] == t_sa].copy()
                if df_ativo.empty or len(df_ativo) < 60: continue
                
                df_ativo.set_index('date', inplace=True)
                df_ativo.index = pd.to_datetime(df_ativo.index)
                df_ativo.rename(columns={'close': 'Close', 'high': 'High', 'low': 'Low', 'open': 'Open', 'volume': 'Volume'}, inplace=True)
                
                try:
                    analysis = opt_engine.analyze_volatility_and_squeeze(df_ativo)
                    ticker_clean = t_sa.replace('.SA', '')
                    records.append(RankOptionsAnalysis(
                        ticker=ticker_clean,
                        hv20=analysis.get('hv20', 0.0),
                        hv50=analysis.get('hv50', 0.0),
                        vol_status=analysis.get('vol_status', ''),
                        squeeze_on=bool(analysis.get('squeeze_on', False)),
                        direction=analysis.get('direction', ''),
                        qullamaggie_status=analysis.get('qullamaggie', {}).get('breakout', {}).get('status', ''),
                        momentum_60d=analysis.get('qullamaggie', {}).get('momentum_60d', 0.0),
                        is_ep=bool(analysis.get('qullamaggie', {}).get('episodic_pivot', {}).get('active', False)),
                        is_parabolic=bool(analysis.get('qullamaggie', {}).get('parabolic_short', {}).get('active', False))
                    ))
                except Exception as e:
                    logger.error(f"Error processing {t_sa} for options: {e}")
                    
        if records:
            db.bulk_save_objects(records)
        logger.info(f"Inserted {len(records)} Options Analysis records.")
    except Exception as e:
        logger.error(f"Error in update_rank_options_analysis: {e}")

def update_rank_monthly_allocation(db: Session):
    logger.info("Updating Monthly Allocation Ranking...")
    engine = MonthlyBdrEngine()
    db.query(RankMonthlyAllocation).delete()
    
    # Save base ranking. API will multiply by capital. We save top 50 of each type to be safe.
    br_picks = engine.calculate_momentum_score(engine.get_top_br_stocks(), "AÇÃO BR", top_n=50)
    bdr_picks = engine.calculate_momentum_score(engine.bdrs_pool, "BDR USA", top_n=50)
    
    records = []
    if not br_picks.empty:
        for idx, row in br_picks.iterrows():
            records.append(RankMonthlyAllocation(
                ticker=row['ticker'],
                peso_sugerido=row.get('rank_score', 0.0), # Save score here, frontend/API sorts by it
                tipo_ativo="BR",
                preco=row.get('preco', 0.0),
                tendencia=row.get('tendencia', '')
            ))
            
    if not bdr_picks.empty:
        for idx, row in bdr_picks.iterrows():
            records.append(RankMonthlyAllocation(
                ticker=row['ticker'],
                peso_sugerido=row.get('rank_score', 0.0),
                tipo_ativo="BDR",
                preco=row.get('preco', 0.0),
                tendencia=row.get('tendencia', '')
            ))
            
    if records:
        db.bulk_save_objects(records)
    logger.info(f"Inserted {len(records)} Monthly Allocation records.")

def run_all_jobs():
    init_db()
    db = SessionLocal()
    try:
        update_rank_alpha_selection(db)
        update_rank_long_short(db)
        update_rank_options_analysis(db)
        update_rank_monthly_allocation(db)
        db.commit()
        logger.info("All rankings updated successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error running batch jobs: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_all_jobs()