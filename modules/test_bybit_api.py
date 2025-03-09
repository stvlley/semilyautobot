#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from pybit.unified_trading import HTTP

# Load environment variables
load_dotenv()

# Retrieve API credentials
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")

if not BYBIT_API_KEY or not BYBIT_API_SECRET:
    print("Bybit API credentials not found in the .env file.")
    exit(1)

# 🚀 ✅ Corrected: Remove 'endpoint', it is no longer used!
session = HTTP(api_key=BYBIT_API_KEY, api_secret=BYBIT_API_SECRET)

print("Testing Bybit API connection...")

# Test: Get USDT wallet balance (for Derivatives account, accountType "CONTRACT")
try:
    response = session.get_wallet_balance(accountType="CONTRACT", coin="USDT")
    print("Wallet Balance Response:")
    print(response)
except Exception as e:
    print("Error while testing API:", e)