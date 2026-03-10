#Breanna Cuellar and Rachel Cavanaugh

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import math


@dataclass
class FreshmanClassYearRecord:
    year: int
    enrolled: int
    housing_capacity: int
    housing_cost_per_student: float


class CollegeData:
    def __init__(
        self,
        records: List[FreshmanClassYearRecord],
        capacity_threshold: float = 1.00,
        growth_threshold: float = 0.05,
    ) -> None:
        self.records = sorted(records, key=lambda r: r.year)
        self.by_year: Dict[int, FreshmanClassYearRecord] = {r.year: r for r in self.records}
        self.capacity_threshold = capacity_threshold
        self.growth_threshold = growth_threshold

    def enrollment_growth(self) -> List[Tuple[int, Optional[float]]]:
        result: List[Tuple[int, Optional[float]]] = []
        prev: Optional[FreshmanClassYearRecord] = None

        for r in self.records:
            if prev is None or prev.enrolled == 0:
                result.append((r.year, None))
            else:
                pct = (r.enrolled - prev.enrolled) / prev.enrolled
                result.append((r.year, pct))
            prev = r

        return result

    def space_pressure(self) -> List[Tuple[int, float, int]]:
        result: List[Tuple[int, float, int]] = []
        for r in self.records:
            if r.housing_capacity <= 0:
                result.append((r.year, math.inf, r.enrolled))
                continue
            ratio = r.enrolled / r.housing_capacity
            overflow = max(0, r.enrolled - r.housing_capacity)
            result.append((r.year, ratio, overflow))
        return result

    def housing_revenue_estimate(self, year: Optional[int] = None) -> float:
        if year is not None:
            r = self.by_year[year]
            return float(r.enrolled) * float(r.housing_cost_per_student)
        return sum(float(r.enrolled) * float(r.housing_cost_per_student) for r in self.records)

    def percent_increase_revenue(self, lookback_years: int = 4) -> List[Tuple[int, Optional[float]]]:
        years = [r.year for r in self.records]
        result: List[Tuple[int, Optional[float]]] = []

        for i, y in enumerate(years):
            j = i - lookback_years
            if j < 0:
                result.append((y, None))
                continue

            rev_now = self.housing_revenue_estimate(y)
            rev_then = self.housing_revenue_estimate(years[j])
            result.append((y, None if rev_then == 0 else (rev_now - rev_then) / rev_then))

        return result
