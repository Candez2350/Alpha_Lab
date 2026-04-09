import traceback
from core.engine_ls import LongShortEngine
from core.engine_opt import OptionsEngine
from core.constants import IBRX_100
import core.yf_setup as yf

print("--- Testing L&S Scan ---")
try:
    engine = LongShortEngine()
    df_prices = engine.get_market_data(IBRX_100[:5]) # just 5 to test
    print("Market data fetched")
    opportunities = engine.scan_opportunities(df_prices, capital_total=20000)
    print("Opportunities scanned:", len(opportunities))
except Exception as e:
    print("L&S Error:")
    traceback.print_exc()

print("--- Testing Vol Radar ---")
try:
    engine = OptionsEngine()
    data = yf.download("BOVA11.SA", period="6mo", progress=False)
    if data.empty:
        print("Ativo não encontrado")
    else:
        analysis = engine.analyze_volatility_and_squeeze(data)
        print("Analysis done:", analysis.keys())
except Exception as e:
    print("Vol Radar Error:")
    traceback.print_exc()
