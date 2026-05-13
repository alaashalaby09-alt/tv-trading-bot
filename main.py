from fastapi import FastAPI, Request

app = FastAPI()

# =========================
# Storage
# =========================

state = {}

# شكل البيانات:
# {
#   "AAPL": {
#       "pending_1h": True,
#       "position": "none"
#   }
# }

# =========================
# Root
# =========================

@app.get("/")
async def root():
    return {"status": "running"}

# =========================
# Webhook
# =========================

@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()

    symbol = data.get("symbol")
    signal_type = data.get("type")
    timeframe = data.get("timeframe")

    # إنشاء حالة للسهم إذا غير موجود
    if symbol not in state:
        state[symbol] = {
            "pending_1h": False,
            "position": "none"
        }

    stock = state[symbol]

    print("\n========================")
    print(f"NEW ALERT: {data}")

    # =========================
    # ENTRY SIGNALS
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
                    stock["pending_1h"] = False

                    print(f"[{symbol}] ENTER TRADE")

                else:

                    print(f"[{symbol}] ALREADY IN POSITION")

            else:

                print(f"[{symbol}] NO 1H CONFIRMATION")

    # =========================
    # EXIT SIGNALS
    # =========================

    elif signal_type == "exit":

        if stock["position"] == "long":

            stock["position"] = "none"
            stock["pending_1h"] = False

            print(f"[{symbol}] EXIT TRADE")

        else:

            print(f"[{symbol}] NO ACTIVE POSITION")

    # =========================
    # DEBUG STATE
    # =========================

    print(f"STATE: {state}")

    return {
        "success": True,
        "state": state
    }
