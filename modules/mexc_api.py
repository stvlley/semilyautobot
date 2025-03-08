# modules/mexc_api.py

import os
import time
import ccxt
from dotenv import load_dotenv

load_dotenv()

REQUEST_COUNT = 0
LAST_RESET_TIME = time.time()

API_MAX_REQUESTS = 1000
API_WINDOW_SECONDS = 60

def check_usage():
    global REQUEST_COUNT, LAST_RESET_TIME
    now = time.time()
    # If our time window expired, reset usage
    if now - LAST_RESET_TIME > API_WINDOW_SECONDS:
        REQUEST_COUNT = 0
        LAST_RESET_TIME = now

    # Optional: warn if close to limit
    if REQUEST_COUNT >= 0.8 * API_MAX_REQUESTS:
        print(f"[WARNING] {REQUEST_COUNT}/{API_MAX_REQUESTS} requests used in this window.")

def increment_usage():
    global REQUEST_COUNT
    check_usage()
    REQUEST_COUNT += 1

MEXC_API_KEY = os.getenv("MEXC_API_KEY", "")
MEXC_API_SECRET = os.getenv("MEXC_API_SECRET", "")

exchange = ccxt.mexc({
    "apiKey": MEXC_API_KEY,
    "secret": MEXC_API_SECRET,
    "enableRateLimit": True,
})

def fetch_current_price(symbol: str) -> float:
    """
    Returns the latest last price for 'symbol' (e.g., "BTC/USDT").
    Returns None on error.
    """
    try:
        increment_usage()
        ticker = exchange.fetch_ticker(symbol)
        return ticker["last"]
    except Exception as e:
        print(f"Error fetching {symbol} on MEXC: {e}")
        return None

# If run directly, test
if __name__ == "__main__":
    price = fetch_current_price("BTC/USDT")
    if price is not None:
        print(f"BTC/USDT = {price}")
        print(f"Requests used: {REQUEST_COUNT}/{API_MAX_REQUESTS}")
    else:
        print("Failed to fetch BTC price.")
