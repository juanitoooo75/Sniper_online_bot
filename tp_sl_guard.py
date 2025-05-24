import time
import json
from web3 import Web3
from dotenv import load_dotenv
import os
from sniper_sell import sell_token
from notifier import send_telegram

load_dotenv()

RPC_URL = os.getenv("RPC_URL")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
web3 = Web3(Web3.HTTPProvider(RPC_URL))

ROUTER_ADDRESS = Web3.to_checksum_address("0x10ED43C718714eb63d5aA57B78B54704E256024E")
WBNB = Web3.to_checksum_address("0xBB4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c")

ROUTER_ABI = json.loads("""[
  {
    "inputs": [
      {"internalType":"uint256","name":"amountIn","type":"uint256"},
      {"internalType":"address[]","name":"path","type":"address[]"}
    ],
    "name":"getAmountsOut",
    "outputs":[{"internalType":"uint256[]","name":"","type":"uint256[]"}],
    "stateMutability":"view",
    "type":"function"
  }
]""")

router = web3.eth.contract(address=ROUTER_ADDRESS, abi=ROUTER_ABI)

def get_token_value(token_address, amount):
    try:
        path = [Web3.to_checksum_address(token_address), WBNB]
        out = router.functions.getAmountsOut(amount, path).call()
        return web3.from_wei(out[-1], "ether")
    except:
        return 0

print("🧠 TP/SL Guard activé...")
while True:
    try:
        with open("wallet_tracker.json", "r") as f:
            tokens = json.load(f)
    except:
        tokens = []

    for token in tokens:
        token_address = token["token"]
        buy_amount = token["amount"]  # en wei
        buy_price = float(token["buy_price"])  # en BNB

        current_value = get_token_value(token_address, int(buy_amount))

        if current_value == 0:
            print(f"⚠️ Impossible d’évaluer le token {token_address}")
            continue

        gain_pct = ((current_value - buy_price) / buy_price) * 100

        print(f"📈 Token {token_address[:6]}... | Gain : {gain_pct:.2f}%")

        if gain_pct >= 30:
            print(f"✅ TP atteint : {gain_pct:.2f}% → vente")
            send_telegram(f"🎯 TP +{gain_pct:.2f}% atteint → vente en cours")
            sell_token(token_address, web3)
        elif gain_pct <= -20:
            print(f"🛑 SL atteint : {gain_pct:.2f}% → vente")
            send_telegram(f"⚠️ SL {gain_pct:.2f}% atteint → vente en cours")
            sell_token(token_address, web3)

    time.sleep(20)
