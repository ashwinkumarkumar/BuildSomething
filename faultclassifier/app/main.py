from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from .classifier import predict
from .models import FeatureInput, PredictionResponse
from .db import db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.post("/", response_model=PredictionResponse)
def predict_fault(features: FeatureInput):
    try:
        # Step 1: Run classifier
        pred, prob = predict(features.dict())
        condition = "broken" if pred == 1 else "healthy"

        # Step 2: Log to MongoDB
        features_dict = features.dict()
        fft_peaks = features_dict.pop("fft_peaks")
        features_dict["fft1"] = fft_peaks[0] if len(fft_peaks) > 0 else 0.0
        features_dict["fft2"] = fft_peaks[1] if len(fft_peaks) > 1 else 0.0
        features_dict["fft3"] = fft_peaks[2] if len(fft_peaks) > 2 else 0.0
        log_data = {
            "features": features_dict,
            "prediction": {
                "condition": condition,
                "probability": prob
            },
            "created_at": datetime.utcnow().isoformat()
        }
        db.predictions.insert_one(log_data)

        return PredictionResponse(condition=condition, probability=prob)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
