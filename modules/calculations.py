# modules/calculations.py

from modules.mexc_api import fetch_current_price

def calc_profit(entry_price, exit_price, leverage, capital, position_type):
    notional = capital * leverage
    if position_type.upper() == "LONG":
        fraction = (exit_price - entry_price) / entry_price
    else:  # SHORT
        fraction = (entry_price - exit_price) / entry_price
    return notional * fraction

def calc_liquidation(entry_price, leverage, position_type):
    if position_type.upper() == "LONG":
        return entry_price * (1 - 1/leverage)
    else:
        return entry_price * (1 + 1/leverage)

def run_calculation_flow():
    """
    1) Show BTC price
    2) Ask coin -> fetch + override
    3) Ask position type, exit price, leverage, capital
    4) Show profit + liquidation
    """
    print("\n=== CALCULATION FLOW ===")

    # Show BTC
    btc_price = fetch_current_price("BTC/USDT")
    if btc_price is not None:
        print(f"BTC/USDT: {btc_price:.3f} USDT")
    else:
        print("WARNING: Failed to fetch BTC price.")

    # Ask coin
    coin = input("Coin ticker (e.g. SOL) or 'menu': ").strip().upper()
    if coin.lower() == "menu":
        print("Returning to main menu.\n")
        return
    symbol_pair = f"{coin}/USDT"

    # Fetch coin price
    coin_price = fetch_current_price(symbol_pair)
    if coin_price is None:
        print(f"Failed to fetch {symbol_pair}. Using 0.0.")
        coin_price = 0.0
    else:
        print(f"{symbol_pair}: {coin_price:.3f} USDT")

    override = input("Press ENTER to accept or 'override' to change entry: ").strip().lower()
    if override == "override":
        while True:
            val = input("Custom entry price or 'menu': ").strip()
            if val.lower() == "menu":
                print("Returning to main menu.\n")
                return
            try:
                coin_price = float(val)
                break
            except ValueError:
                print("Invalid numeric input.")

    print(f"ENTRY PRICE set to {coin_price:.3f} for {symbol_pair}.\n")

    # Now gather the rest
    while True:
        pos = input("Position (LONG/SHORT) or 'menu': ").strip().upper()
        if pos.lower() == "menu":
            print("Returning.\n")
            return
        if pos in ["LONG", "SHORT"]:
            break
        print("Invalid. Must be LONG or SHORT.")

    while True:
        val = input("Exit price or 'menu': ").strip()
        if val.lower() == "menu":
            print("Returning.\n")
            return
        try:
            exit_price = float(val)
            break
        except ValueError:
            print("Invalid numeric input.")

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

    # Compute
    profit = calc_profit(coin_price, exit_price, leverage, capital, pos)
    liq = calc_liquidation(coin_price, leverage, pos)

    print("\n--- RESULTS ---")
    print(f"Position={pos}, Entry={coin_price:.3f}, Exit={exit_price:.3f}, Leverage={leverage}, Capital={capital}")
    print(f"Potential Profit: {profit:.2f} USDT")
    print(f"Approx Liquidation: {liq:.3f} USDT\n")

    input("Press ENTER to return to main menu.\n")
