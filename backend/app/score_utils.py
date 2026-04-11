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
    clamped = max(MIN_OPEN_SCORE, min(score, MAX_OPEN_SCORE))
    quantized = round(clamped, SCORE_DECIMALS)
    return max(MIN_OPEN_SCORE, min(quantized, MAX_OPEN_SCORE))


def format_open_score(value: float, decimals: int = SCORE_DECIMALS) -> str:
    """
    Format score as fixed-point decimal in [0.1, 0.9].
    """
    clamped = clamp_open_score(value)
    rounded = round(clamped, decimals)
    quantum = 10 ** (-decimals)
    if rounded < MIN_OPEN_SCORE:
        rounded = MIN_OPEN_SCORE if decimals == SCORE_DECIMALS else MIN_OPEN_SCORE + quantum
    elif rounded > MAX_OPEN_SCORE:
        rounded = MAX_OPEN_SCORE if decimals == SCORE_DECIMALS else MAX_OPEN_SCORE - quantum
    return f"{rounded:.{decimals}f}"
