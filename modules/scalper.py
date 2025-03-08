# modules/scalper.py

import time
from modules.mexc_api import fetch_current_price
from modules.calculations import calc_profit, calc_liquidation

def start_scalping(symbol: str, position_type: str, capital: float, leverage: float, target_fraction: float, entry_price: float):
    """
    A basic example: fetch current price every 5s, compare with 'entry_price'.
    If price moves >= target_fraction from entry, we exit.
    """
    print(f"Scalper started for {symbol}, pos={position_type}, entry={entry_price:.3f}, target={target_fraction:.4f}\n")

    while True:
        current_price = fetch_current_price(symbol)
        if current_price is None:
            print("Failed to fetch current price. Sleeping 5s.")
            time.sleep(5)
            continue

        if position_type.upper() == "LONG":
            fraction = (current_price - entry_price) / entry_price
        else:  # SHORT
            fraction = (entry_price - current_price) / entry_price

        print(f"{symbol}={current_price:.3f}, move={fraction*100:.2f}% (target={target_fraction*100:.2f}%)")

        if fraction >= target_fraction:
            # exit
            profit = calc_profit(entry_price, current_price, leverage, capital, position_type)
            liq = calc_liquidation(entry_price, leverage, position_type)
            print(f"\nTarget reached! Profit={profit:.2f} USDT, Liquidation={liq:.3f} USDT\n")
            break

        time.sleep(5)

def run_scalper_flow():
    """
    1) Show BTC price
    2) Ask coin -> fetch + override
    3) Then ask pos/capital/leverage/fraction
    4) start_scalping
    """
    print("\n=== SCALPER FLOW ===")

    # BTC
    btc_price = fetch_current_price("BTC/USDT")
    if btc_price is not None:
        print(f"BTC/USDT: {btc_price:.3f} USDT")
    else:
        print("WARNING: Failed to fetch BTC price.")

    # Coin
    coin = input("Coin ticker (e.g. SOL) or 'menu': ").strip().upper()
    if coin.lower() == "menu":
        print("Returning.\n")
        return
    symbol_pair = f"{coin}/USDT"

    # Fetch coin price
    coin_price = fetch_current_price(symbol_pair)
    if coin_price is None:
        print(f"Failed to fetch {symbol_pair}. Using 0.0 fallback.")
        coin_price = 0.0
    else:
        print(f"{symbol_pair}: {coin_price:.3f} USDT")

    override = input("Press ENTER to accept or 'override' to change entry: ").strip().lower()
    if override == "override":
        while True:
            val = input("Custom entry or 'menu': ").strip()
            if val.lower() == "menu":
                print("Returning.\n")
                return
            try:
                coin_price = float(val)
                break
            except ValueError:
                print("Invalid numeric input.")

    print(f"ENTRY PRICE set to {coin_price:.3f} for {symbol_pair}.\n")

    # Ask position
    while True:
        pos = input("Position (LONG/SHORT) or 'menu': ").strip().upper()
        if pos.lower() == "menu":
            print("Returning.\n")
            return
        if pos in ["LONG", "SHORT"]:
            break
        print("Invalid. Must be LONG or SHORT.")

    # Ask capital
    while True:
        val = input("Capital (USDT) or 'menu': ").strip()
        if val.lower() == "menu":
            print("Returning.\n")
            return
        try:
            capital = float(val)
            break
        except ValueError:
            print("Invalid numeric input.")

    # Ask leverage
    while True:
        val = input("Leverage or 'menu': ").strip()
        if val.lower() == "menu":
            print("Returning.\n")
            return
        try:
            leverage = float(val)
            break
        except ValueError:
            print("Invalid numeric input.")

    # Ask fraction
    while True:
        val = input("Target fraction (e.g. 0.001) or 'menu': ").strip()
        if val.lower() == "menu":
            print("Returning.\n")
            return
        try:
            fraction = float(val)
            break
        except ValueError:
            print("Invalid numeric input.")

    print("\nStarting scalper now...\n")
    start_scalping(symbol_pair, pos, capital, leverage, fraction, entry_price=coin_price)

    print("\nScalper done. Returning to main menu.\n")
