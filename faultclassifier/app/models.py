from pydantic import BaseModel
from typing import List

class FeatureInput(BaseModel):
    rms: float
    kurtosis: float
    skewness: float
    std_dev: float
    fft_peaks: List[float]

class PredictionResponse(BaseModel):
    condition: str
    probability: float
