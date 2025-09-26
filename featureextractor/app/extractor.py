# app/extractor.py
from typing import Dict, List, Union
import math
import numpy as np
import scipy.stats as stats
from .utils import detrend_center, top_n_indices, ensure_nonnegative_int

def compute_rms(signal: List[float]) -> float:
    if not signal:
        return 0.0
    return np.sqrt(np.mean(np.array(signal)**2))


def compute_std(signal: List[float]) -> float:
    if len(signal) <= 1:
        return 0.0
    return np.std(signal, ddof=0)


def compute_skewness(signal: List[float]) -> float:
    if len(signal) <= 2:
        return 0.0
    return stats.skew(signal)


def compute_kurtosis(signal: List[float]) -> float:
    if len(signal) <= 3:
        return 0.0
    return stats.kurtosis(signal)


def compute_fft_peaks(signal: List[float], sampling_rate: float, n_peaks: int = 3) -> List[float]:
    """
    Compute normalized magnitude spectrum (0..1) and return top-n peak magnitudes (excluding DC).
    The output matches your requested shape: a list of magnitudes, not frequencies.
    """
    n = len(signal)
    if n < 4:
        return [0.0] * n_peaks

    # Detrend (center) to reduce DC bias
    sig = np.asarray(detrend_center(signal), dtype=np.float64)

    # Real FFT and corresponding magnitude spectrum
    spectrum = np.fft.rfft(sig)
    mags = np.abs(spectrum)

    # Exclude DC bin when ranking peaks
    if mags.size > 1:
        mags_no_dc = mags[1:]
    else:
        mags_no_dc = mags

    if mags_no_dc.size == 0:
        return [0.0] * n_peaks

    # Normalize magnitudes to [0, 1] for a compact, scale-free feature
    max_mag = mags_no_dc.max() if mags_no_dc.max() > 0 else 1.0
    mags_norm = mags_no_dc / max_mag

    # Pick top-n magnitudes
    n_peaks = ensure_nonnegative_int(n_peaks, default=3, min_n=1, max_n=10)
    peak_indices = top_n_indices(mags_norm.tolist(), n_peaks)
    # Keep order by descending magnitude
    peak_vals = [float(mags_norm[i]) for i in peak_indices]
    return peak_vals


def extract_features(acceleration: List[float], sampling_rate: float, n_fft_peaks: int = 3) -> Dict[str, Union[float, List[float]]]:
    """
    Compute the full feature vector required by the classifier stage.
    """
    rms = compute_rms(acceleration)
    std_dev = compute_std(acceleration)
    skewness = compute_skewness(acceleration)
    kurtosis = compute_kurtosis(acceleration)
    fft_peaks = compute_fft_peaks(acceleration, sampling_rate, n_peaks=n_fft_peaks)

    return {
        "rms": rms,
        "kurtosis": kurtosis,
        "skewness": skewness,
        "std_dev": std_dev,
        "fft_peaks": fft_peaks
    }