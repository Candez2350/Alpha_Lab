import sys
import logging
from core.engine_ls import LongShortEngine

logging.basicConfig(level=logging.DEBUG)

try:
    engine = LongShortEngine()
    print("Fetching market data...")
    # Just 3 tickers to make it fast
    df_prices = engine.get_market_data(["PETR4", "VALE3", "ITUB4"])
    print("Data fetched. Scanning opportunities...")
    opps = engine.scan_opportunities(df_prices, capital_total=20000.0)
    print("Scan complete.")
    print(opps)
except Exception as e:
    import traceback
    traceback.print_exc()
