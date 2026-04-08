import yfinance as yf
data = yf.download("BOVA11.SA", period="6mo", progress=False)
print(data.columns)
print(data.head(2))
