#Breanna Cuellar and Rachel Cavanaugh

from typing import List, Optional, Tuple
import sys

from models import FreshmanClassYearRecord, CollegeData

import file_handling_reference as io_utils

import survey_references as survey_impl


def demo_records() -> List[FreshmanClassYearRecord]:
    return [
        FreshmanClassYearRecord(2021, 5476, 4386, 9642),
        FreshmanClassYearRecord(2022, 5103, 4386, 10964),
        FreshmanClassYearRecord(2023, 5540, 4386, 11940),
        FreshmanClassYearRecord(2024, 5271, 4386, 13825.5),
        FreshmanClassYearRecord(2025, 5811, 4386, 15882)
    ]


def demo_survey_rows() -> List[dict]:
    stress_col = "How does the crowdedness affect your stress level?"

    exp_col = "How would you rate your experience on a scale from 1 to 5?"

    dorm_col = "Which dorm are you in?"

    return [
        {dorm_col: "single", exp_col: "2", stress_col: "5"},
        {dorm_col: "double", exp_col: "3", stress_col: "4"},
        {dorm_col: "triple", exp_col: "2", stress_col: "4"},
        {dorm_col: "quad",   exp_col: "4", stress_col: "3"},
        {dorm_col: "quint",  exp_col: "1", stress_col: "5"},
    ]


# ---------- Column detection helpers ----------
def pick_first_existing_column(row: dict, options: List[str], fallback: str) -> str:
    """Return the first column name that exists in the row; else fallback."""
    for col in options:
        if col in row:
            return col
    return fallback


def detect_survey_columns(survey_rows: List[dict]) -> Tuple[str, str, str]:
    """Detect likely column names based on the first row's keys."""
    if not survey_rows:
        # fall back to survey_references defaults
        return (
            "Which dorm are you in?",
            "How would you rate your experience on a scale from 1 to 5?",
            "How does the crowdedness affect your stress level?",
        )

    first = survey_rows[0]

    dorm_col = pick_first_existing_column(
        first,
        options=[
            "Which dorm are you in?",
            "Which dorm are you in",
            "Dorm",
            "dorm",
        ],
        fallback="Which dorm are you in?",
    )

    exp_col = pick_first_existing_column(
        first,
        options=[
            "How would you rate your experience on a scale from 1 to 5?",
            "How would you rate your experience?",
            "How would you rate your experience",
            "experience",
            "Experience",
        ],
        fallback="How would you rate your experience on a scale from 1 to 5?",
    )

    stress_col = pick_first_existing_column(
        first,
        options=[
            "How does the crowdedness affect your stress level?",
            "How does the crowdedness affect your stress level",
            "stress",
            "Stress",
        ],
        fallback="How does the crowdedness affect your stress level?",
    )

    return dorm_col, exp_col, stress_col


# ---------- Stress factor ----------
def calculate_stress_level_factor(survey_rows: List[dict], stress_col: str) -> Optional[float]:
    """
    Average stress (1–5) normalized to a 0–1 scale:
      1 -> 0.00, 3 -> 0.50, 5 -> 1.00
    """
    if not survey_rows:
        return None

    vals: List[int] = []
    for row in survey_rows:
        s = survey_impl.one_to_five(row.get(stress_col, ""))
        if s is not None:
            vals.append(s)

    if not vals:
        return None

    avg_stress = sum(vals) / len(vals)
    return (avg_stress - 1) / 4


# ---------- Report builders ----------
def build_basic_report(college: CollegeData) -> List[str]:
    lines: List[str] = []
    lines.append("Milestone Project — Limited Housing → Overcrowding + Student Distress")
    lines.append("Theme: Limited Housing causes overcrowded dorms and distress to residents.")
    lines.append("")

    lines.append("=== Capacity Strain (Space Pressure) ===")
    for year, ratio, overflow in college.space_pressure():
        flag = "OVER CAPACITY" if ratio > college.capacity_threshold else "OK"
        lines.append(f"{year}: pressure={ratio:.2f} (enrolled/capacity), overflow≈{overflow} → {flag}")
    lines.append("")

    lines.append("=== Enrollment Growth (Year-over-Year) ===")
    for year, pct in college.enrollment_growth():
        if pct is None:
            lines.append(f"{year}: N/A (first year)")
        else:
            flag = "HIGH GROWTH" if pct > college.growth_threshold else "normal"
            lines.append(f"{year}: {pct*100:.2f}% → {flag}")
    lines.append("")

    lines.append("=== Housing Revenue Estimate ===")
    for r in college.records:
        rev = college.housing_revenue_estimate(r.year)
        lines.append(f"{r.year}: ${rev:,.2f}")
    lines.append("")

    lines.append("=== Revenue % Increase vs 4 Years Ago ===")
    for year, pct in college.percent_increase_revenue(lookback_years=4):
        if pct is None:
            lines.append(f"{year}: N/A (not enough history)")
        else:
            lines.append(f"{year}: {pct*100:.2f}%")
    lines.append("")

    return lines


def append_survey_report_lines(lines: List[str], college: CollegeData, survey_rows: List[dict]) -> None:
    lines.append("=== Survey Outputs ===")

    dorm_col, exp_col, stress_col = detect_survey_columns(survey_rows)

    # Stress Factor (0–1)
    stress_factor = calculate_stress_level_factor(survey_rows, stress_col=stress_col)
    lines.append(
        f"Stress Level Factor (0–1 severity): {stress_factor:.2f}"
        if stress_factor is not None
        else "Stress Level Factor: N/A"
    )

    # Percent stressed
    percent = survey_impl.percent_stressed(survey_rows, stress_col=stress_col, stressed_threshold=4)
    lines.append(f"Percent stressed (stress >= 4): {percent:.1f}%" if percent is not None else "Percent stressed: N/A")

    # Average stress (1–5)
    stress_vals = [
        survey_impl.one_to_five(r.get(stress_col, "")) for r in survey_rows
    ]
    stress_vals = [v for v in stress_vals if v is not None]
    avg_stress = (sum(stress_vals) / len(stress_vals)) if stress_vals else None
    lines.append(f"Average stress level: {avg_stress:.2f}/5" if avg_stress is not None else "Average stress level: N/A")

    # Average happiness (experience only)
    happiness_vals: List[float] = []
    for row in survey_rows:
        happiness, _ = survey_impl.compute_happiness_from_experience(row, experience_col=exp_col)
        happiness_vals.append(happiness)
    avg_h = (sum(happiness_vals) / len(happiness_vals)) if happiness_vals else None
    lines.append(f"Average happiness (experience-only): {avg_h:.1f}/100" if avg_h is not None else "Average happiness: N/A")

    # Per respondent
    base_cost = college.records[-1].housing_cost_per_student if college.records else 0.0
    lines.append("")
    lines.append("Per-respondent (stress + cost estimate + happiness):")

    for i, row in enumerate(survey_rows, start=1):
        stress_num = survey_impl.one_to_five(row.get(stress_col, ""))
        stress_str = f"{stress_num}/5" if stress_num is not None else "N/A"

        happiness, _ = survey_impl.compute_happiness_from_experience(row, experience_col=exp_col)
        cost = survey_impl.estimate_student_housing_cost(row, default_cost=base_cost, dorm_col=dorm_col)

        lines.append(f"  Respondent #{i}: stress={stress_str} | cost≈${cost:,.2f} | happiness={happiness:.1f}/100")

    lines.append("")


def make_report(college: CollegeData, survey_rows: Optional[List[dict]] = None) -> str:
    lines = build_basic_report(college)

    if survey_rows is not None:
        append_survey_report_lines(lines, college, survey_rows)

    lines.append("=== Social Responsibility Insight ===")
    lines.append(
        "This analysis highlights an ethical tension: increasing enrollment can increase housing revenue, "
        "but if housing capacity does not keep up, overcrowding rises and student stress may increase."
    )
    return "\n".join(lines)


# ---------- Main ----------
def main(argv: Optional[List[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    # Demo mode (prints survey + stress factor)
    if len(argv) == 0:
        college = CollegeData(demo_records())
        survey_rows = demo_survey_rows()
        report = make_report(college, survey_rows=survey_rows)
        print(report)
        io_utils.write_text_summary("summary.txt", report)
        return 0

    if len(argv) not in (1, 2):
        print("Usage:\n  python main.py\n  python main.py year_data.csv [survey_responses.csv]")
        return 2

    year_path = argv[0]
    survey_path = argv[1] if len(argv) == 2 else None

    try:
        records = io_utils.read_year_data_csv(year_path)
    except Exception as e:
        print(f"Failed to read year data CSV '{year_path}': {e}")
        return 3

    college = CollegeData(records)

    survey_rows = None
    if survey_path:
        try:
            survey_rows = io_utils.read_survey_csv(survey_path)
        except Exception as e:
            print(f"Failed to read survey CSV '{survey_path}': {e}")
            survey_rows = None

    report = make_report(college, survey_rows=survey_rows)
    print(report)

    try:
        io_utils.write_text_summary("summary.txt", report)
    except Exception as e:
        print(f"Warning: could not write summary.txt: {e}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
