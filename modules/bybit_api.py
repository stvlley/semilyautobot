# modules/bybit_api.py

import os
import ccxt
from dotenv import load_dotenv

load_dotenv()

BYBIT_API_KEY = os.getenv("BYBIT_API_KEY", "")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET", "")

exchange = ccxt.bybit({
    "apiKey": BYBIT_API_KEY,
    "secret": BYBIT_API_SECRET,
    "enableRateLimit": True,
})

def fetch_latest_price(symbol: str) -> float:
    """
    Fetch the latest 'last' price for 'symbol' (e.g., "BTC/USDT") from Bybit.
    Returns None if any error occurs.
    """
    try:
        ticker = exchange.fetch_ticker(symbol)
        return ticker['last']  # ccxt typically uses 'last' for last traded price
    except Exception as e:
        print(f"Error fetching Bybit price for {symbol}: {e}")
        return None
