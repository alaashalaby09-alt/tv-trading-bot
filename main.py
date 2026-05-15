from fastapi import FastAPI, Request
import json
import os

app = FastAPI()

STATE_FILE = "state.json"

# =========================
# Load State
# =========================

def load_state():

    if os.path.exists(STATE_FILE):

        with open(STATE_FILE, "r") as f:
            return json.load(f)

    return {}

# =========================
# Save State
# =========================

def save_state(state):

    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

# =========================
# Global State
# =========================

state = load_state()

# =========================
# Root
# =========================

@app.get("/")
async def root():
    return {
        "status": "running",
        "state": state
    }

# =========================
# Webhook
# =========================

@app.post("/webhook")
async def webhook(request: Request):

    global state

    data = await request.json()

    symbol = data.get("symbol")
    signal_type = data.get("type")
    timeframe = data.get("timeframe")

    # =========================
    # Create Symbol State
    # =========================

    if symbol not in state:

        state[symbol] = {
            "pending_1h": False,
            "position": "none"
        }

    stock = state[symbol]

    print("\n========================")
    print(f"NEW ALERT: {data}")

    # =========================
    # ENTRY
    # =========================

    if signal_type == "entry":

        # 1H confirmation
        if timeframe == "1H":

            stock["pending_1h"] = True

            print(f"[{symbol}] 1H CONFIRMED")

        # 15m execution
        elif timeframe == "15m":

            if stock["pending_1h"]:

                if stock["position"] == "none":

                    stock["position"] = "long"

                    print(f"[{symbol}] ENTER TRADE")

                else:

                    print(f"[{symbol}] ALREADY IN POSITION")

            else:

                print(f"[{symbol}] NO 1H CONFIRMATION")

    # =========================
    # EXIT
    # =========================

    elif signal_type == "exit":

        if stock["position"] == "long":

            stock["position"] = "none"
            stock["pending_1h"] = False

            print(f"[{symbol}] EXIT TRADE")

        else:

            print(f"[{symbol}] NO ACTIVE POSITION")

    # =========================
    # SAVE STATE
    # =========================

    save_state(state)

    # =========================
    # DEBUG
    # =========================

    print(f"STATE: {state}")

    return {
        "success": True,
        "state": state
    }
