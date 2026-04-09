import yfinance as yf_module
import time
import pandas as pd
import requests_cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure session with caching and a realistic User-Agent to avoid YFRateLimitError
session = requests_cache.CachedSession('http_cache', expire_after=3600)
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "*/*"
})

_cache = {}
CACHE_TTL = 3600 # 1 hour

def download(tickers, *args, **kwargs):
    if isinstance(tickers, list) or isinstance(tickers, tuple):
        key_str = ",".join(sorted([str(t) for t in tickers]))
    else:
        key_str = str(tickers)
        
    cache_key = f"{key_str}_{kwargs.get('period', 'max')}_{kwargs.get('interval', '1d')}"
    
    now = time.time()
    if cache_key in _cache:
        data, timestamp = _cache[cache_key]
        if now - timestamp < CACHE_TTL:
            return data.copy()
            
    # Add a small delay to avoid hitting limits when fetching new data
    time.sleep(0.5)
    
    try:
        kwargs['session'] = session
        if 'progress' not in kwargs:
            kwargs['progress'] = False
        data = yf_module.download(tickers, *args, **kwargs)
        _cache[cache_key] = (data, now)
        return data
    except Exception as e:
        # If rate limited, maybe return cached data if available regardless of TTL
        if cache_key in _cache:
            return _cache[cache_key][0].copy()
        raise e

def Ticker(*args, **kwargs):
    kwargs['session'] = session
    return yf_module.Ticker(*args, **kwargs)
