from fastapi import FastAPI

app = FastAPI(title="AI Daily Digest API", version="1.0.0")


@app.get("/api/health")
async def api_health():
    return {"status": "ok"}
