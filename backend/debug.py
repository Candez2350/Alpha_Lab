import core.yf_setup as yf
import pandas as pd
import fundamentus

try:
    print("--- OPT ---")
    df = yf.download("BOVA11.SA", period="6mo", progress=False)
    print(type(df['Close']))
    if isinstance(df['Close'], pd.DataFrame):
        print("Close is DataFrame")
    else:
        print("Close is Series")
except Exception as e:
    print("OPT Error:", e)

try:
    print("--- SELECTION ---")
    df = fundamentus.get_resultado()
    print("Columns:", df.columns)
    print("Index name:", df.index.name)
except Exception as e:
    print("SELECTION Error:", e)

