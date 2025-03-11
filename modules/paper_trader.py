#!/usr/bin/env python3
import os
import csv
import time
import datetime
import signal
import pandas as pd
import numpy as np
import ta
from dotenv import load_dotenv
from pybit.unified_trading import HTTP

# ✅ Load API keys from .env
load_dotenv()
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY", "")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET", "")

# ✅ Initialize Bybit Testnet API connection
session = HTTP(
    demo=True,  
    api_key=BYBIT_API_KEY,
    api_secret=BYBIT_API_SECRET,
    recv_window=10000
)

# ✅ Define the CSV file path for logging trades
csv_file_path = os.path.join(os.getcwd(), "paper_trades.csv")

total_profit = 0  # Track total earnings over time
open_trade = None  # Track open trade
trade_history = []  # Store trade history for learning
running = True  # Control for stopping bot

def signal_handler(sig, frame):
    global running, open_trade
    confirm = input("\n⚠️ Are you sure you want to stop the bot? (yes/no): ")
    if confirm.lower() == "yes":
        print("\n🔴 Stopping bot...")
        if open_trade:
            print("📉 Closing open trade before exit...")
            close_trade()
        print(f"💰 Total Profit so far: ${total_profit:.2f}")
        running = False
    else:
        print("✅ Bot continues running...")

signal.signal(signal.SIGINT, signal_handler)


def fetch_latest_price(symbol):
    """✅ Fetch latest market price."""
    try:
        response = session.get_tickers(category="linear", symbol=symbol)
        return float(response["result"]["list"][0]["lastPrice"])
    except Exception as e:
        print(f"⚠ Error fetching price for {symbol}: {e}")
        return None


def get_minimum_order_size(symbol: str):
    """✅ Fetch the minimum order size and step size from Bybit for a given symbol."""
    try:
        response = session.get_instruments_info(category="linear", symbol=symbol)
        instrument = response["result"]["list"][0]
        min_qty = float(instrument["lotSizeFilter"]["minOrderQty"])
        qty_step = float(instrument["lotSizeFilter"]["qtyStep"])
        return min_qty, qty_step
    except Exception as e:
        print(f"⚠ Error fetching minimum order size for {symbol}: {e}")
        return 0.001, 0.001  # Safe default values


def suggest_leverage_and_capital():
    """✅ Suggest leverage and capital based on past trades and allow user confirmation."""
    global trade_history
    leverage = 5  # Default leverage
    capital = 500  # Default capital allocation
    
    if trade_history:
        last_trade = trade_history[-1]
        if last_trade['pnl'] > 0:
            leverage = min(last_trade['leverage'] + 1, 10)  # Increase leverage if profitable
            capital += 50  # Increase capital slightly if profitable
        else:
            leverage = max(last_trade['leverage'] - 1, 3)  # Reduce leverage on losses
            capital = max(100, capital - 50)  # Reduce capital to manage risk
    
    print(f"🔍 Suggested Leverage: {leverage}x, Suggested Capital: ${capital}")
    
    modify = input("🔸 Do you want to modify these values? (yes/no): ")
    if modify.lower() == "yes":
        leverage = int(input("🔸 Enter new leverage (max 20x): "))
        leverage = min(max(leverage, 1), 20)  # Ensure leverage is between 1x and 20x
        capital = float(input("🔸 Enter new capital (max $5000): "))
        capital = min(max(capital, 100), 5000)  # Ensure capital is between $100 and $5000
    
    print(f"✅ Final Decision: {leverage}x leverage, ${capital} capital.")
    return leverage, capital


def place_trade(symbol, side, leverage, capital):
    """✅ Places a market order on Bybit Testnet with validated leverage and capital."""
    global open_trade
    price = fetch_latest_price(symbol)
    if not price:
        print("❌ Cannot fetch latest price. Skipping trade.")
        return None
    
    min_qty, qty_step = get_minimum_order_size(symbol)
    quantity = round((capital * leverage) / price, 3)
    
    # Adjust quantity to fit Bybit's step size rules
    if quantity < min_qty:
        quantity = min_qty
    elif quantity % qty_step != 0:
        quantity = round(quantity - (quantity % qty_step), 3)
    
    print(f"📈 Placing {side} trade on {symbol} at ${price:.2f} with qty={quantity}, leverage={leverage}x")
    
    try:
        session.place_order(category="linear", symbol=symbol, side=side, orderType="Market", qty=quantity)
        open_trade = {"symbol": symbol, "side": side, "entry_price": price, "leverage": leverage, "quantity": quantity}
        return open_trade
    except Exception as e:
        print(f"❌ Trade failed: {e}")
        return None


def close_trade():
    """✅ Closes the open trade before stopping the bot."""
    global open_trade, trade_history, total_profit
    if not open_trade:
        return
    
    exit_price = fetch_latest_price(open_trade["symbol"])
    if not exit_price:
        print("❌ Cannot fetch exit price. Holding position.")
        return
    
    pnl = (exit_price - open_trade["entry_price"]) * open_trade["quantity"] * open_trade["leverage"]
    total_profit += pnl
    trade_history.append({"symbol": open_trade["symbol"], "pnl": pnl, "leverage": open_trade["leverage"]})
    
    session.place_order(category="linear", symbol=open_trade["symbol"], side="Sell" if open_trade["side"] == "Buy" else "Buy", orderType="Market", qty=open_trade["quantity"])
    print(f"💰 Closing trade at ${exit_price:.2f} | PnL: ${pnl:.2f}")
    open_trade = None


def run_paper_trader(symbol):
    """✅ Runs the scalping bot."""
    global running
    leverage, capital = suggest_leverage_and_capital()
    print(f"✅ Final Decision: Trading {symbol} with {leverage}x leverage and ${capital} capital.")
    
    while running:
        open_trade = place_trade(symbol, "Buy", leverage, capital)  # Placeholder logic
        if open_trade:
            print("⏳ Holding trade... Checking for exit conditions...")
            time.sleep(60)
            close_trade()
        time.sleep(60)


# ✅ Ask user for the token
symbol = input("\n🔸 Enter the symbol to trade (e.g., ETHUSDT, SOLUSDT): ").upper()
run_paper_trader(symbol)
