# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from app.simulator import get_signal
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import random

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27018")

mongo_client = MongoClient(MONGO_URI)
db = mongo_client.gearbox

app = FastAPI(
    title="Signal Generator Service",
    description="Generates vibration signals for gearbox fault detection",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response schema
class SignalResponse(BaseModel):
    data: List[float]

@app.get("/api/signal", response_model=SignalResponse)
def generate_signal(label: str, sensor_count: int = 1):
    try:
        data = get_signal(label, sensor_count)
        return SignalResponse(data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/test", response_model=SignalResponse)
def get_test_signal(label: str):
    try:
        doc = db.test_signals_broken.aggregate([{"$match": {"label": label}}, {"$sample": {"size": 1}}]).next()
        return {"data": doc.get("sensors", [])}
    except StopIteration:
        raise HTTPException(status_code=404, detail=f"No signal found for label '{label}'")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
