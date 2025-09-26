# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Union, Optional
from .utils import validate_signal, validate_sampling_rate
from .extractor import extract_features

app = FastAPI(
    title="Feature Extractor Service",
    description="Computes diagnostic features from raw vibration signals",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request and response schemas
class ExtractRequest(BaseModel):
    data: List[float] = Field(..., description="List of sensor values")

class ExtractResponse(BaseModel):
    rms: float
    kurtosis: float
    skewness: float
    std_dev: float
    fft_peaks: List[float]


@app.post("/", response_model=ExtractResponse)
def extract(req: ExtractRequest):
    try:
        signal = validate_signal(req.data)
        sr = validate_sampling_rate(None, default=30.0)
        feats = extract_features(signal, sr, n_fft_peaks=3)
        return ExtractResponse(**feats)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/")
def health():
    return {"service": "feature-extractor", "status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8100, reload=True)