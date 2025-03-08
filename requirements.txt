def main():
    print("Running...")

    try:
        # Ask for user inputs
        token = input("Enter the token symbol (e.g., SOL): ").strip().upper()
        entry_price = float(input("What is your entry price? "))
        exit_price = float(input("What is your exit price? "))
        leverage = float(input("What is your leverage? "))
        capital = float(input("What is your capital (in USDT)? "))

        # Basic calculation (similar to before)
        notional = capital * leverage
        price_move = (exit_price - entry_price) / entry_price  # as a decimal
        potential_profit = notional * price_move

        # Print summary
        print("\n=== Scalping Summary ===")
        print(f"Token:           {token}")
        print(f"Entry Price:     {entry_price} USDT")
        print(f"Exit Price:      {exit_price} USDT")
        print(f"Leverage:        x{leverage}")
        print(f"Capital:         {capital} USDT")
        print(f"Notional Value:  {notional} USDT")
        print(f"Potential % Move: {price_move * 100:.2f}%")
        print(f"Potential Profit (approx.): {potential_profit:.2f} USDT")

    except ValueError as e:
        # If the user inputs invalid numbers, you'll land here.
        print(f"Invalid input: {e}")

if __name__ == "__main__":
    main()
