# modules/current_price.py

from modules.mexc_api import fetch_current_price

def run_current_price_flow():
    """
    1) Show BTC price
    2) Ask user for coin -> fetch price -> optional override
    3) Repeatedly show updated coin price each time user presses ENTER
    4) 'menu' returns to main menu
    """
    print("\n=== CURRENT PRICE FLOW ===")

    # 1. BTC price
    btc_price = fetch_current_price("BTC/USDT")
    if btc_price is not None:
        print(f"BTC/USDT current price: {btc_price:.3f} USDT")
    else:
        print("WARNING: Failed to fetch BTC price.")

    # 2. Ask coin
    coin = input("Which coin are you trading? (e.g. SOL) or 'menu' to go back: ").strip().upper()
    if coin.lower() == "menu":
        print("Returning to main menu.\n")
        return
    symbol_pair = f"{coin}/USDT"

    # 3. Fetch coin price
    coin_price = fetch_current_price(symbol_pair)
    if coin_price is None:
        print(f"Failed to fetch {symbol_pair}. Using 0.0 as fallback.")
        coin_price = 0.0
    else:
        print(f"{symbol_pair} current price: {coin_price:.3f} USDT")

    override = input("Press ENTER to accept or type 'override' to change entry price: ").strip().lower()
    if override == "override":
        while True:
            val = input("Enter custom entry price or 'menu': ").strip()
            if val.lower() == "menu":
                print("Returning to main menu.\n")
                return
            try:
                coin_price = float(val)
                break
            except ValueError:
                print("Invalid. Try again.")

    print(f"ENTRY PRICE set to {coin_price:.3f} for {symbol_pair}.\n")

    # 4. Repeatedly show updated coin price
    while True:
        user = input("[ENTER to refresh | 'menu' to return]: ").strip().lower()
        if user == "menu":
            print("Returning to main menu.\n")
            break
        if user != "":
            print("Invalid input (ENTER or 'menu').")
            continue

        # Fetch again
        price = fetch_current_price(symbol_pair)
        if price is not None:
            print(f"{symbol_pair} = {price:.3f} USDT (entry={coin_price:.3f})")
        else:
            print(f"Failed to fetch {symbol_pair}.")
