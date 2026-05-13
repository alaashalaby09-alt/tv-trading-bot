from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "running"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    print("==== NEW ALERT ====")
    print(data)

    return {
        "success": True,
        "received": data
    }
