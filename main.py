from fastapi import FastAPI, Request
import json
import os

app = FastAPI()

STATE_FILE = "state.json"

# =========================
# TIMEFRAMES
# =========================

HTF = "1H"
LTF = "15m"

# =========================
# LOAD STATE
# =========================

def load_state():

    if os.path.exists(STATE_FILE):

        with open(STATE_FILE, "r") as f:
            return json.load(f)

    return {}

# =========================
# SAVE STATE
# =========================

def save_state(state):

    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

# =========================
# GLOBAL STATE
# =========================

state = load_state()

# =========================
# ROOT
# =========================

@app.get("/")
async def root():

    return {
        "status": "running",
        "HTF": HTF,
        "LTF": LTF,
        "state": state
    }

# =========================
# WEBHOOK
# =========================

@app.post("/webhook")
async def webhook(request: Request):

    global state

    data = await request.json()

    symbol = data.get("symbol")
    signal_type = data.get("type")
    timeframe = data.get("timeframe")
    side = data.get("side")

    if not symbol:

        return {
            "success": False,
            "error": "missing symbol"
        }

    # =========================
    # CREATE SYMBOL
    # =========================

    if symbol not in state:

        state[symbol] = {
            "pending_htf": False,
            "position": "none"
        }

    stock = state[symbol]

    print("\n========================")
    print(f"NEW ALERT: {data}")

    # =========================
    # ENTRY
    # =========================

    if signal_type == "entry":

        # HTF CONFIRMATION

        if timeframe == HTF:

            stock["pending_htf"] = True

            print(f"[{symbol}] HTF CONFIRMED")

        # LTF EXECUTION

        elif timeframe == LTF:

            if stock["pending_htf"]:

                if stock["position"] == "none":

                    stock["position"] = "long"

                    print(f"[{symbol}] ENTER TRADE")

                else:

                    print(f"[{symbol}] ALREADY IN POSITION")

            else:

                print(f"[{symbol}] NO HTF CONFIRMATION")

    # =========================
    # EXIT
    # =========================

    elif signal_type == "exit":

        if stock["position"] == "long":

            stock["position"] = "none"

            # بعد الخروج ننتظر تأكيد HTF جديد
            stock["pending_htf"] = False

            print(f"[{symbol}] EXIT TRADE")

        else:

            print(f"[{symbol}] NO ACTIVE POSITION")

    # =========================
    # SAVE
    # =========================

    save_state(state)

    print(f"STATE: {state}")

    return {
        "success": True,
        "state": state
    }
