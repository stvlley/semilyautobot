import sys
from modules.current_price import run_current_price_flow
from modules.calculations import run_calculation_flow
from modules.scalper import run_scalper_flow

# Import the paper trader
from modules.paper_trader import run_paper_trader
from modules.bybit_api import fetch_latest_price  # optional for quick API test

def main_menu():
    while True:
        print("=== MAIN MENU ===")
        print("1) Current Price Flow")
        print("2) Calculation Flow")
        print("3) Scalper Flow")
        print("4) Paper Trader (Bybit)")
        print("5) Exit")

        choice = input("Select an option: ").strip()
        print()
        if choice == "1":
            run_current_price_flow()
        elif choice == "2":
            run_calculation_flow()
        elif choice == "3":
            run_scalper_flow()
        elif choice == "4":
            paper_trader_menu()
        elif choice == "5":
            print("Exiting. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice.\n")

def paper_trader_menu():
    """
    Dedicated flow for Bybit paper trading config:
    - Symbol, interval, duration, capital
    - Quick API test
    - run_paper_trader
    """
    print("=== PAPER TRADER (BYBIT) ===")

    # Symbol
    symbol = input("Bybit symbol (default 'BTC/USDT'): ").strip()
    if not symbol:
        symbol = "BTC/USDT"

    # Interval
    try:
        interval_str = input("Interval in seconds (default=300 for 5m): ").strip()
        if interval_str:
            interval_sec = int(interval_str)
        else:
            interval_sec = 300
    except ValueError:
        interval_sec = 300
        print("Invalid input. Using 300s.")

    # Duration
    try:
        duration_str = input("Total duration in seconds (default=1800 for 30m): ").strip()
        if duration_str:
            total_duration_sec = int(duration_str)
        else:
            total_duration_sec = 1800
    except ValueError:
        total_duration_sec = 1800
        print("Invalid input. Using 1800s.")

    # Capital
    try:
        cap_str = input("Capital (default=1000): ").strip()
        if cap_str:
            capital = float(cap_str)
        else:
            capital = 1000.0
    except ValueError:
        capital = 1000.0
        print("Invalid input. Using 1000.")

    # Quick test of the Bybit API
    test_price = fetch_latest_price(symbol)
    if test_price is None:
        print(f"**WARNING**: Could not fetch price for {symbol}. Check API or symbol.")
    else:
        print(f"Quick test: {symbol} price is {test_price:.2f} USDT")

    # Show summary
    print(f"\nStarting PAPER TRADER with:")
    print(f" Symbol:     {symbol}")
    print(f" Interval:   {interval_sec} sec")
    print(f" Duration:   {total_duration_sec} sec")
    print(f" Capital:    {capital}")
    print("====================================\n")

    try:
        run_paper_trader(
            symbol=symbol,
            interval_sec=interval_sec,
            total_duration_sec=total_duration_sec,
            capital=capital
        )
        print("Paper trading session finished.\n")
    except KeyboardInterrupt:
        print("\nPaper trader stopped (Ctrl+C). Returning to menu.\n")


def main():
    print("Welcome to the Autobot!")
    main_menu()

if __name__ == "__main__":
    main()
