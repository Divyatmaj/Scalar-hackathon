import math


MIN_OPEN_SCORE = 1e-6
MAX_OPEN_SCORE = 1.0 - MIN_OPEN_SCORE


def clamp_open_score(value: float) -> float:
    """
    Clamp numeric score into strict open interval (0, 1).
    """
    score = float(value)
    if not math.isfinite(score):
        raise ValueError(f"Score must be finite, got: {score}")
    return max(MIN_OPEN_SCORE, min(score, MAX_OPEN_SCORE))


def format_open_score(value: float, decimals: int = 6) -> str:
    """
    Format score as fixed-point decimal that remains strictly in (0, 1).
    """
    clamped = clamp_open_score(value)
    rounded = round(clamped, decimals)
    quantum = 10 ** (-decimals)
    if rounded <= 0.0:
        rounded = quantum
    elif rounded >= 1.0:
        rounded = 1.0 - quantum
    return f"{rounded:.{decimals}f}"
