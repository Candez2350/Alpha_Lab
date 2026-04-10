import os
import pandas as pd
import yfinance as yf
import fundamentus
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from core.db import engine, DailyPrice, Fundamental, BDR, IBRX100
from core.constants import BDR_TICKERS

def run_sync_pipeline(db: Session):
    print("Starting sync pipeline...")
    
    # 1. Sync Fundamentals & IBRX 100
    print("Fetching fundamentals from Fundamentus...")
    try:
        df_fund = fundamentus.get_resultado()
        df_fund.columns = [col.replace('.', '').replace('/', '').lower() for col in df_fund.columns]
        
        # Fetch sectors
        bancos = []
        utils = []
        seguros = []
        try: bancos = fundamentus.list_papel_setor(35)
        except: pass
        try: utils = fundamentus.list_papel_setor(14)
        except: pass
        try: seguros = fundamentus.list_papel_setor(38)
        except: pass
        
        # Clear existing fundamentals
        db.query(Fundamental).delete()
        
        fund_records = []
        for ticker, row in df_fund.iterrows():
            setor = None
            if ticker in bancos: setor = "banco"
            elif ticker in utils: setor = "util"
            elif ticker in seguros: setor = "seguro"
                
            fund_records.append(Fundamental(
                ticker=ticker,
                roic=float(row.get('roic', 0.0) if pd.notna(row.get('roic')) else 0.0),
                evebit=float(row.get('evebit', 0.0) if pd.notna(row.get('evebit')) else 0.0),
                liq2m=float(row.get('liq2m', 0.0) if pd.notna(row.get('liq2m')) else 0.0),
                cotacao=float(row.get('cotacao', 0.0) if pd.notna(row.get('cotacao')) else 0.0),
                setor=setor
            ))
        db.bulk_save_objects(fund_records)
        
        # Rule for IBRX100: Top 100 by liq2m, price > 1.00 (no penny stock)
        # Filter common stocks / units (ends with 3, 4, 11)
        valid_tickers = []
        for t in df_fund.index:
            if t[-1] in ['3', '4', '11'] and not t.endswith('34') and t != 'AURA33':
                valid_tickers.append(t)
        
        df_ibrx = df_fund.loc[valid_tickers]
        df_ibrx = df_ibrx[df_ibrx['cotacao'] > 1.0] # Not penny stock
        df_ibrx = df_ibrx.sort_values(by='liq2m', ascending=False).head(100)
        
        # Ponderação: Valor de mercado (Proxy via pvp * patrliq)
        # Assuming proxy for free float market cap
        df_ibrx['market_cap'] = df_ibrx['pvp'] * df_ibrx['patrliq']
        
        db.query(IBRX100).delete()
        ibrx_records = []
        for ticker, row in df_ibrx.iterrows():
            market_cap_weight = row.get('market_cap', 0.0)
            if pd.isna(market_cap_weight):
                market_cap_weight = 0.0
                
            ibrx_records.append(IBRX100(
                ticker=f"{ticker}.SA",
                weight=float(market_cap_weight)
            ))
        db.bulk_save_objects(ibrx_records)
        print("Fundamentals and IBRX100 synced.")
    except Exception as e:
        print(f"Error syncing fundamentals: {e}")

    # 2. Sync BDRs table
    print("Syncing BDRs table...")
    try:
        db.query(BDR).delete()
        bdr_records = [BDR(ticker=t) for t in BDR_TICKERS]
        db.bulk_save_objects(bdr_records)
        print("BDRs synced.")
    except Exception as e:
        print(f"Error syncing BDRs: {e}")

    db.commit()

    # 3. Sync Daily Prices for IBRX100 and BDRs
    print("Syncing Daily Prices...")
    try:
        all_tickers = [r.ticker for r in db.query(IBRX100).all()] + BDR_TICKERS
        
        # Fetch data for the last 2 years for everyone to ensure enough data for 12M momentum and 200 SMA
        start_date = (datetime.now() - timedelta(days=2*365)).strftime("%Y-%m-%d")
        
        data = yf.download(all_tickers, start=start_date, progress=False)
        
        # Clean up table (in a real scenario we might upsert, but for simplicity and to avoid duplicates we can clear or do a merge)
        # For a full initial sync, clearing might be easier. But let's just use pandas to_sql to replace if it's not too big, 
        # or we iterate and create objects. Since it's around 140 tickers * 500 days = 70,000 rows.
        # It's faster to use pandas.to_sql directly.
        
        df_prices = data.stack(level='Ticker').reset_index()
        df_prices.columns = [c.lower() for c in df_prices.columns]
        df_prices.rename(columns={'date': 'date', 'ticker': 'ticker', 'close': 'close', 'high': 'high', 'low': 'low', 'open': 'open', 'volume': 'volume'}, inplace=True)
        df_prices = df_prices[['date', 'ticker', 'close', 'high', 'low', 'open', 'volume']]
        
        # Convert date to date object
        df_prices['date'] = pd.to_datetime(df_prices['date']).dt.date
        
        # Clear daily prices table and insert
        db.query(DailyPrice).delete()
        db.commit()
        
        df_prices.to_sql('daily_prices', engine, if_exists='append', index=False)
        print("Daily prices synced.")
    except Exception as e:
        print(f"Error syncing daily prices: {e}")
        db.rollback()

    return {"status": "success", "message": "Database sync completed"}
