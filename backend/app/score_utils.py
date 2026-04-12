import math


MIN_OPEN_SCORE = 0.1
MAX_OPEN_SCORE = 0.9


def clamp_open_score(value: float) -> float:
    """
    Clamp numeric score into strict open range [0.1, 0.9].
    NO rounding, NO floor, NO ceil — pure clamp only.
    This is the single source of truth for all score/reward values.
    """
    score = float(value)

    if not math.isfinite(score):
        raise ValueError(f"Score must be finite, got: {score}")

    # Strict clamp — no quantization that could push values to 0.0 or 1.0
    if score < MIN_OPEN_SCORE:
        return MIN_OPEN_SCORE
    if score > MAX_OPEN_SCORE:
        return MAX_OPEN_SCORE

    return score


def format_open_score(value: float, decimals: int = 2) -> str:
    """
    Format score as fixed-point decimal in [0.1, 0.9].
    """
    decimals = max(1, int(decimals))
    clamped = clamp_open_score(value)
    return f"{clamped:.{decimals}f}"
