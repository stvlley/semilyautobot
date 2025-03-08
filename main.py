# main.py
import sys
from modules.current_price import run_current_price_flow
from modules.calculations import run_calculation_flow
from modules.scalper import run_scalper_flow

def main_menu():
    while True:
        print("=== MAIN MENU ===")
        print("1) Current Price Flow")
        print("2) Calculation Flow")
        print("3) Scalper Flow")
        print("4) Exit")

        choice = input("Select an option: ").strip()
        print()
        if choice == "1":
            run_current_price_flow()
        elif choice == "2":
            run_calculation_flow()
        elif choice == "3":
            run_scalper_flow()
        elif choice == "4":
            print("Exiting. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice.\n")

def main():
    print("Welcome to the Autobot!")
    main_menu()

if __name__ == "__main__":
    main()
