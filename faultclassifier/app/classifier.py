import joblib
import numpy as np
import pandas as pd
import os
# Load model once at startup
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
model = joblib.load(MODEL_PATH)


def predict(features: dict):
    fft_peaks = features["fft_peaks"]
    fft1 = fft_peaks[0] if len(fft_peaks) > 0 else 0.0
    fft2 = fft_peaks[1] if len(fft_peaks) > 1 else 0.0
    fft3 = fft_peaks[2] if len(fft_peaks) > 2 else 0.0
    X = pd.DataFrame([[features["rms"], features["kurtosis"], features["skewness"],
                       features["std_dev"], fft1, fft2, fft3]],
                     columns=['rms', 'kurtosis', 'skewness', 'std_dev', 'fft1', 'fft2', 'fft3'])
    pred = model.predict(X)[0]
    prob = model.predict_proba(X)[0][1]
    return pred, prob
