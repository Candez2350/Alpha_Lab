import yfinance as yf_module
import requests_cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os

cache_path = os.path.join(os.path.dirname(__file__), '..', 'http_cache')
session = requests_cache.CachedSession(cache_path, expire_after=3600) # 1 hour cache

retry = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# Update user-agent to prevent default python-requests blocking
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})

def download(*args, **kwargs):
    kwargs['session'] = session
    return yf_module.download(*args, **kwargs)

def Ticker(*args, **kwargs):
    kwargs['session'] = session
    return yf_module.Ticker(*args, **kwargs)
