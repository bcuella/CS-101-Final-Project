#Breanna Cuellar and Rachel Cavanaugh
#AI was used to help import files
import csv
from typing import List
from models import FreshmanClassYearRecord


def read_year_data_csv(path: str) -> List[FreshmanClassYearRecord]:
    with open(path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames:
            raise ValueError("Year CSV file has no headers.")

        fields = {h.strip().lower(): h for h in reader.fieldnames}
        required_columns = ["year", "enrolled", "housing_capacity", "housing_cost_per_student"]

        for col in required_columns:
            if col not in fields:
                raise ValueError(f"Missing column '{col}' in {path}. Found: {reader.fieldnames}")

        records: List[FreshmanClassYearRecord] = []
        for row in reader:
            def get(col: str) -> str:
                return (row[fields[col]] or "").strip()

            records.append(
                FreshmanClassYearRecord(
                    year=int(get("year")),
                    enrolled=int(get("enrolled")),
                    housing_capacity=int(get("housing_capacity")),
                    housing_cost_per_student=float(get("housing_cost_per_student")),
                )
            )

        return records


def read_survey_csv(path: str) -> List[dict]:
    with open(path, "r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_text_summary(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8") as file:
        file.write(text)
