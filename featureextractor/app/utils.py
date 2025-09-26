# app/utils.py
from typing import Iterable, List, Tuple, Union, Optional

def validate_signal(acceleration: Iterable) -> List[float]:
    """
    Validates and converts the input acceleration sequence to a list of floats.
    Raises ValueError if invalid.
    """
    if acceleration is None:
        raise ValueError("Acceleration is required.")
    try:
        seq = list(acceleration)
    except TypeError:
        raise ValueError("Acceleration must be an iterable of numeric values.")

    if len(seq) < 4:
        # A small minimum to allow stable FFT/skew/kurtosis on short signals.
        raise ValueError("Acceleration must contain at least 4 samples.")

    cleaned = []
    for i, v in enumerate(seq):
        try:
            cleaned.append(float(v))
        except (TypeError, ValueError):
            raise ValueError(f"Acceleration value at index {i} is not numeric: {v}")
    return cleaned


def validate_sampling_rate(sampling_rate: Optional[Union[int, float]], default: float = 30.0) -> float:
    """
    Ensures the sampling rate is a positive float. Falls back to default if None.
    """
    if sampling_rate is None:
        return float(default)
    try:
        sr = float(sampling_rate)
    except (TypeError, ValueError):
        raise ValueError("Sampling rate must be numeric.")
    if sr <= 0:
        raise ValueError("Sampling rate must be greater than 0.")
    return sr


def detrend_center(signal: List[float]) -> List[float]:
    """
    Simple mean-centering to remove DC offset before FFT.
    """
    if not signal:
        return signal
    mean_val = sum(signal) / len(signal)
    return [x - mean_val for x in signal]


def top_n_indices(values: List[float], n: int) -> List[int]:
    """
    Return indices of the top-n largest values (descending). Stable ordering by value then index.
    """
    n = max(1, min(n, len(values)))
    return [idx for idx, _ in sorted(enumerate(values), key=lambda p: (-p[1], p[0]))[:n]]


def ensure_nonnegative_int(n: int, default: int = 3, min_n: int = 1, max_n: int = 10) -> int:
    """
    Clamp and sanitize an integer count parameter (e.g., number of FFT peaks).
    """
    try:
        n = int(n)
    except (TypeError, ValueError):
        return default
    return max(min_n, min(n, max_n))