#!/usr/bin/env python3
import os
import time
import signal
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

# ✅ Global State
total_profit = 0
open_trade = None
trade_history = []
running = True


# ✅ Graceful shutdown
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


# ✅ Fetch latest market price
def fetch_latest_price(symbol):
    try:
        response = session.get_tickers(category="linear", symbol=symbol)
        return float(response["result"]["list"][0]["lastPrice"])
    except Exception as e:
        print(f"⚠ Error fetching price for {symbol}: {e}")
        return None


# ✅ Fetch available account balance
def get_available_balance():
    try:
        response = session.get_wallet_balance(accountType="UNIFIED")
        balance_info = response["result"]["list"][0]["totalEquity"]
        return float(balance_info)
    except Exception as e:
        print(f"⚠ Error fetching balance: {e}")
        return 1000  # Safe default value if error occurs


# ✅ Fetch minimum order size and step size
def get_minimum_order_size(symbol):
    try:
        response = session.get_instruments_info(category="linear", symbol=symbol)
        instrument = response["result"]["list"][0]
        min_qty = float(instrument["lotSizeFilter"]["minOrderQty"])
        qty_step = float(instrument["lotSizeFilter"]["qtyStep"])
        return min_qty, qty_step
    except Exception as e:
        print(f"⚠ Error fetching minimum order size for {symbol}: {e}")
        return 0.001, 0.001  # Safe default values


# ✅ Fetch max leverage for symbol
def get_max_leverage(symbol):
    try:
        response = session.get_instruments_info(category="linear", symbol=symbol)
        max_leverage = float(response["result"]["list"][0]["leverageFilter"]["maxLeverage"])
        return max_leverage
    except Exception as e:
        print(f"⚠ Error fetching max leverage for {symbol}: {e}")
        return 20  # Safe default


# ✅ Suggest leverage and capital based on balance
def suggest_leverage_and_capital(symbol):
    global trade_history
    max_leverage = get_max_leverage(symbol)
    available_balance = get_available_balance()

    leverage = min(3, max_leverage)  # ✅ Default to 3x or max allowed
    capital = min(500, available_balance)  # Don't exceed available balance

    # Adjust based on trade history
    if trade_history:
        last_trade = trade_history[-1]
        if last_trade['pnl'] > 0:
            leverage = min(last_trade['leverage'] + 1, max_leverage)
            capital = min(capital + 50, available_balance)
        else:
            leverage = max(last_trade['leverage'] - 1, 1)
            capital = max(100, min(capital - 50, available_balance))

    print(f"💰 Available Balance: ${available_balance:.2f}")
    print(f"🔍 Suggested Leverage: {leverage}x (Max: {max_leverage}x), Suggested Position Size: ${capital}")

    modify = input("🔸 Do you want to modify these values? (yes/no): ").strip().lower()
    if modify == "yes":
        leverage = float(input(f"🔸 Enter leverage (Max {max_leverage}x): "))
        leverage = min(max(leverage, 1), max_leverage)
        capital = float(input(f"🔸 Enter total position size in $ (Max ${available_balance:.2f}): "))
        capital = min(max(capital, 100), available_balance)

    print(f"✅ Final Decision: {leverage}x leverage, total position size: ${capital}")
    return leverage, capital


# ✅ Set leverage for symbol
def set_leverage(symbol, leverage):
    try:
        session.set_leverage(
            symbol=symbol,
            buyLeverage=str(leverage),
            sellLeverage=str(leverage),
            category="linear"
        )
        print(f"✅ Leverage set to {leverage}x for {symbol}")
    except Exception as e:
        print(f"❌ Failed to set leverage: {e}")


# ✅ Place a trade
def place_trade(symbol, side, leverage, capital):
    global open_trade
    price = fetch_latest_price(symbol)
    if not price:
        print("❌ Cannot fetch latest price. Skipping trade.")
        return None

    set_leverage(symbol, leverage)  # ✅ Always set leverage as desired

    min_qty, qty_step = get_minimum_order_size(symbol)
    quantity = round(capital / price, 3)  # ✅ Capital is total position size

    # Adjust quantity to comply with Bybit's requirements
    if quantity < min_qty:
        quantity = min_qty
    elif quantity % qty_step != 0:
        quantity = round(quantity - (quantity % qty_step), 3)

    print(f"📈 Placing {side} trade on {symbol} at ${price:.2f}, qty={quantity}, total position size=${capital}, leverage={leverage}x")

    try:
        session.place_order(
            category="linear",
            symbol=symbol,
            side=side,
            orderType="Market",
            qty=quantity
        )
        open_trade = {"symbol": symbol, "side": side, "entry_price": price, "leverage": leverage, "quantity": quantity}
        return open_trade
    except Exception as e:
        print(f"❌ Trade failed: {e}")
        return None


# ✅ Close the open trade
def close_trade():
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

    side = "Sell" if open_trade["side"] == "Buy" else "Buy"
    session.place_order(category="linear", symbol=open_trade["symbol"], side=side, orderType="Market", qty=open_trade["quantity"])
    print(f"💰 Closed trade at ${exit_price:.2f}, PnL: ${pnl:.2f}")
    open_trade = None


# ✅ Main bot logic
def run_paper_trader(symbol):
    global running
    leverage, capital = suggest_leverage_and_capital(symbol)

    while running:
        trade = place_trade(symbol, "Buy", leverage, capital)
        if trade:
            print("⏳ Holding trade... Checking for exit conditions...")
            time.sleep(60)
            close_trade()
        time.sleep(60)


# ✅ Start bot
if __name__ == "__main__":
    symbol = input("\n🔸 Enter the symbol to trade (e.g., ETHUSDT, SOLUSDT): ").upper().strip()
    run_paper_trader(symbol)