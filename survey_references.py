#Breanna Cuellar and Rachel Cavanaugh
from typing import Dict, List, Optional, Tuple



def one_to_five(value: str) -> Optional[int]:
    v = (value or "").strip()
    if not v:
        return None
    try:
        n = int(float(v))
        if 1 <= n <= 5:
            return n
    except ValueError:
        return None
    return None


def compute_happiness_from_experience(
    row: dict,
    experience_col: str = "How would you rate your experience on a scale from 1 to 5?"
) -> Tuple[float, Dict[str, float]]:
    experience = one_to_five(row.get(experience_col, ""))

    breakdown: Dict[str, float] = {"experience": 0.0}
    if experience is not None:
        breakdown["experience"] = ((experience - 1) / 4) * 100

    score = breakdown["experience"]
    score = max(0.0, min(100.0, score))
    return score, breakdown


def percent_stressed(
    survey_rows: List[dict],
    stress_col: str = "How does the crowdedness affect your stress level?",
    stressed_threshold: int = 4
) -> Optional[float]:
    if not survey_rows:
        return None

    valid = 0
    stressed = 0

    for row in survey_rows:
        s = one_to_five(row.get(stress_col, ""))
        if s is None:
            continue
        valid += 1
        if s >= stressed_threshold:
            stressed += 1

    if valid == 0:
        return None
    return (stressed / valid) * 100.0


def estimate_student_housing_cost(
    row: dict,
    default_cost: float,
    dorm_col: str = "Which dorm are you in?"
) -> float:
    dorm = (row.get(dorm_col, "") or "").strip().lower()

    actual_costs = {
        "single": 14000.0,
        "double": 13284.0,
        "triple": 12380.0,
        "quad": 12000.0,
        "quadruple": 12000.0,
        "quint": 11000.0,
        "quintuple": 11000.0,
    }

    # If dorm type not found, fall back to the yearly default cost from your dataset
    return actual_costs.get(dorm, float(default_cost))
