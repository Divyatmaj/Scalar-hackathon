import math


MIN_OPEN_SCORE = 0.1
MAX_OPEN_SCORE = 0.9
SCORE_DECIMALS = 1


def clamp_open_score(value: float) -> float:
    """
    Clamp numeric score into strict range [0.1, 0.9] and quantize to 1 decimal.
    """
    score = float(value)
    if not math.isfinite(score):
        raise ValueError(f"Score must be finite, got: {score}")
    score = max(MIN_OPEN_SCORE, min(score, MAX_OPEN_SCORE))
    factor = 10 ** SCORE_DECIMALS
    score = math.floor(score * factor) / factor
    score = max(MIN_OPEN_SCORE, min(score, MAX_OPEN_SCORE))
    return score


def format_open_score(value: float, decimals: int = SCORE_DECIMALS) -> str:
    """
    Format score as fixed-point decimal in [0.1, 0.9].
    """
    clamped = clamp_open_score(value)
    return f"{clamped:.{decimals}f}"
