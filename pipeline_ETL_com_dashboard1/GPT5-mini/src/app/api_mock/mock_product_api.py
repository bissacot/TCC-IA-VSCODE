from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pathlib import Path
import json

app = FastAPI(title="Mock Product API")

DATA_PATH = Path(__file__).resolve().parents[3] / "data" / "products.json"


@app.get("/products")
async def get_products():
    if DATA_PATH.exists():
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return JSONResponse(content=data)
    return JSONResponse(content=[]) 
