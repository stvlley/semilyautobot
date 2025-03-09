#!/usr/bin/env python3
import os
from time import sleep
from dotenv import load_dotenv
from pybit.unified_trading import WebSocket,HTTP


# Load environment variables
load_dotenv()

# Retrieve API credentials
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")

# Initialize HTTP session for REST API (to get wallet balance)
session = HTTP(
    demo=True,
    api_key=BYBIT_API_KEY,  
    api_secret=BYBIT_API_SECRET,
    recv_window=10000
)


# response = session.get_wallet_balance(accountType="UNIFIED")
# print(response)
try:
    response = session.get_wallet_balance(accountType="UNIFIED")
    
    if "result" in response and "list" in response["result"]:
        account_data = response["result"]["list"][0]  # First account in the list
        
        if "coin" in account_data:
            for coin in account_data["coin"]:  # Iterate over the coins
                if coin["coin"] == "USDT":  # Find USDT balance
                    usdt_balance = coin["walletBalance"]
                    print(f"✅ USDT Wallet Balance: {usdt_balance}")
                    break
            else:
                print("⚠️ USDT balance not found.")
        else:
            print("⚠️ 'coin' key not found in account data.")
    else:
        print("⚠️ 'result' or 'list' key not found in response.")

    # print("🔹 Full API Response:", response)  # Debugging

except Exception as e:
    print("⚠️ Full Error Response:", e)

