# modules/paper_trader.py

import os
import csv
import time
import datetime
import random
import ccxt
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv()
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY", "")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET", "")

# Initialize Bybit testnet API connection
exchange = ccxt.bybit({
    "apiKey": BYBIT_API_KEY,
    "secret": BYBIT_API_SECRET,
    "enableRateLimit": True,
    "options": {
        "defaultType": "swap",  # Ensure we're using the correct market type (USDT perpetual)
    }
})
exchange.set_sandbox_mode(True)  # Activate Testnet Mode

def run_paper_trader(symbol: str, interval_sec: int = 300, total_duration_sec=3600, capital: float = 1000.0):
    """
    Runs a testnet trading bot that executes real trades on Bybit's demo environment.
    - Places market BUY and SELL orders based on a simple strategy.
    - Uses leverage dynamically.
    - Logs trades into a CSV file.
    """

    start_time = time.time()
    trades_csv = "paper_trades.csv"

    position_open = False
    entry_price = 0.0
    position_side = None
    leverage = 1.0

    print(f"\n🚀 ** TESTNET PAPER TRADER for {symbol} **")
    print(f"Interval={interval_sec}s | Duration={total_duration_sec}s | Capital={capital}")
    print(f"Bybit Testnet API Key: {BYBIT_API_KEY[:5]}... (hidden)")
    print("(Press Ctrl+C to stop early)\n")

    while True:
        if time.time() - start_time > total_duration_sec:
            print("🔴 Reached total_duration_sec. Stopping paper trader.")
            break

        # Fetch latest price from Bybit testnet
        price = fetch_latest_price(symbol)
        if price is None:
            print(f"⚠ Failed to fetch price for {symbol}. Retrying in 60s.")
            time.sleep(60)
            continue

        # Evaluate entry signals
        risk_score = evaluate_signals(price, symbol)
        chosen_leverage = choose_leverage(risk_score)

        if not position_open:
            if risk_score > 0.7:
                # OPEN LONG position
                position_open = True
                position_side = "LONG"
                entry_price = price
                leverage = chosen_leverage

                # Calculate quantity based on capital
                quantity = (capital * leverage) / price

                # Send order to Bybit testnet
                try:
                    order = exchange.create_order(
                        symbol=symbol,
                        type="market",
                        side="buy",
                        amount=quantity
                    )
                    print(f"✅ [TESTNET] Market BUY Order Placed | Qty={quantity:.6f} | {symbol}")
                except Exception as e:
                    print(f"❌ Error placing test BUY order: {e}")

                # Log the trade
                trade_data = {
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "symbol": symbol,
                    "side": position_side,
                    "action": "OPEN",
                    "price": price,
                    "leverage": leverage,
                    "pnl": 0.0
                }
                log_trade_csv(trades_csv, trade_data)
                print(f"📈 OPEN LONG at {price:.2f} | Leverage: x{leverage}")

        else:
            # If position is open, check exit condition
            if risk_score < 0.4:
                position_open = False
                exit_price = price
                pnl = compute_pnl(position_side, entry_price, exit_price, leverage, capital)

                # Place SELL order to close position
                quantity = (capital * leverage) / entry_price
                try:
                    order = exchange.create_order(
                        symbol=symbol,
                        type="market",
                        side="sell",
                        amount=quantity
                    )
                    print(f"✅ [TESTNET] Market SELL Order Placed | Qty={quantity:.6f} | {symbol}")
                except Exception as e:
                    print(f"❌ Error placing test SELL order: {e}")

                # Log the trade
                trade_data = {
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "symbol": symbol,
                    "side": position_side,
                    "action": "CLOSE",
                    "price": price,
                    "leverage": leverage,
                    "pnl": pnl
                }
                log_trade_csv(trades_csv, trade_data)
                print(f"📉 CLOSE {position_side} at {price:.2f} | PnL={pnl:.2f}")

                # Reset state
                position_side = None
                entry_price = 0.0
                leverage = 1.0

        # Sleep before next trade check
        time.sleep(interval_sec)

def fetch_latest_price(symbol: str) -> float:
    """
    Fetches the latest market price for a given symbol from Bybit Testnet.
    """
    try:
        ticker = exchange.fetch_ticker(symbol)
        return ticker['last']
    except Exception as e:
        print(f"⚠ Error fetching Bybit price for {symbol}: {e}")
        return None

def evaluate_signals(price: float, symbol: str) -> float:
    """
    Uses a simple placeholder strategy to return a risk score (0.0 - 1.0).
    0.0 = Strong SELL, 1.0 = Strong BUY.
    """
    return random.random()

def choose_leverage(risk_score: float) -> float:
    """
    Determines leverage dynamically based on risk confidence.
    - risk_score = 0 => leverage = 1
    - risk_score = 1 => leverage = 20
    """
    return 1 + (19 * risk_score)

def compute_pnl(side: str, entry: float, exit_: float, lev: float, capital: float) -> float:
    """
    Calculates a simple profit/loss for the position.
    """
    notional = capital * lev
    if side == "LONG":
        fraction = (exit_ - entry) / entry
    else:
        fraction = (entry - exit_) / entry
    return notional * fraction

def log_trade_csv(filename: str, trade_data: dict):
    """Appends trade data to a CSV file."""
    file_exists = os.path.isfile(filename)
    with open(filename, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=trade_data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(trade_data)

# Quick test
if __name__ == "__main__":
    run_paper_trader("BTC/USDT", interval_sec=60, total_duration_sec=600, capital=500)
    