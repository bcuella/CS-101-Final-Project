#Breanna Cuellar and Rachel Cavanaugh

import os
import math
import unittest
import tempfile
from contextlib import redirect_stdout
from io import StringIO
import main

from models import FreshmanClassYearRecord, CollegeData


class TestProject(unittest.TestCase):
    def make_records_unsorted(self):
        return [
            FreshmanClassYearRecord(2023, 6700, 5400, 13000.0),
            FreshmanClassYearRecord(2021, 6000, 5200, 12000.0),
            FreshmanClassYearRecord(2025, 7600, 5400, 14000.0),
            FreshmanClassYearRecord(2022, 6300, 5200, 12500.0),
            FreshmanClassYearRecord(2024, 7100, 5400, 13500.0),
        ]

    def test_freshman_record_fields(self):
        r = FreshmanClassYearRecord(2021, 6000, 5200, 12000.0)
        self.assertEqual(r.year, 2021)
        self.assertEqual(r.enrolled, 6000)
        self.assertEqual(r.housing_capacity, 5200)
        self.assertEqual(r.housing_cost_per_student, 12000.0)

    def test_college_data_sorts_records_and_builds_by_year(self):
        college = CollegeData(self.make_records_unsorted())

        years = [r.year for r in college.records]
        self.assertEqual(years, [2021, 2022, 2023, 2024, 2025])

        self.assertEqual(set(college.by_year.keys()), {2021, 2022, 2023, 2024, 2025})
        self.assertEqual(college.by_year[2024].enrolled, 7100)

    def test_enrollment_growth_values(self):
        college = CollegeData(self.make_records_unsorted())
        growth = college.enrollment_growth()

        expected = [
            (2021, None),
            (2022, (6300 - 6000) / 6000),
            (2023, (6700 - 6300) / 6300),
            (2024, (7100 - 6700) / 6700),
            (2025, (7600 - 7100) / 7100),
        ]

        self.assertEqual(len(growth), len(expected))
        for (y1, pct1), (y2, pct2) in zip(growth, expected):
            self.assertEqual(y1, y2)
            if pct2 is None:
                self.assertIsNone(pct1)
            else:
                self.assertAlmostEqual(pct1, pct2, places=12)

    def test_space_pressure_ratio_and_overflow(self):
        college = CollegeData(self.make_records_unsorted())
        sp = college.space_pressure()

        expected = {
            2021: (6000 / 5200, 800),
            2022: (6300 / 5200, 1100),
            2023: (6700 / 5400, 1300),
            2024: (7100 / 5400, 1700),
            2025: (7600 / 5400, 2200),
        }

        self.assertEqual(len(sp), 5)
        for year, ratio, overflow in sp:
            exp_ratio, exp_overflow = expected[year]
            self.assertAlmostEqual(ratio, exp_ratio, places=12)
            self.assertEqual(overflow, exp_overflow)

    def test_space_pressure_zero_capacity_is_inf_and_overflow_equals_enrolled(self):
        college = CollegeData([FreshmanClassYearRecord(2021, 100, 0, 1000.0)])
        sp = college.space_pressure()
        year, ratio, overflow = sp[0]

        self.assertEqual(year, 2021)
        self.assertTrue(math.isinf(ratio))
        self.assertEqual(overflow, 100)

    def test_housing_revenue_estimate_by_year(self):
        college = CollegeData(self.make_records_unsorted())
        self.assertAlmostEqual(college.housing_revenue_estimate(2024), 7100 * 13500.0, places=7)

    def test_housing_revenue_estimate_total(self):
        college = CollegeData(self.make_records_unsorted())
        total = sum(r.enrolled * r.housing_cost_per_student for r in college.records)
        self.assertAlmostEqual(college.housing_revenue_estimate(), total, places=7)

    def test_percent_increase_revenue_lookback_4(self):
        college = CollegeData(self.make_records_unsorted())
        out = college.percent_increase_revenue(lookback_years=4)

        # First 4 years should be None
        for year, pct in out[:4]:
            self.assertIsNone(pct)

        rev2025 = 7600 * 14000.0
        rev2021 = 6000 * 12000.0
        expected_pct = (rev2025 - rev2021) / rev2021

        self.assertEqual(out[-1][0], 2025)
        self.assertAlmostEqual(out[-1][1], expected_pct, places=12)

    # ---------- Main tests ----------
    def test_demo_mode_prints_stress_factor_and_writes_summary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)

                buf = StringIO()
                with redirect_stdout(buf):
                    exit_code = main.main([])

                output = buf.getvalue()

                self.assertEqual(exit_code, 0)
                self.assertIn("=== Survey Outputs ===", output)
                self.assertIn("Stress Level Factor", output)

                self.assertTrue(os.path.exists("summary.txt"))
                with open("summary.txt", "r", encoding="utf-8") as f:
                    text = f.read()
                self.assertIn("Stress Level Factor", text)

            finally:
                os.chdir(old_cwd)

    def test_csv_mode_prints_stress_factor_and_writes_summary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)

                year_path = os.path.join(tmpdir, "year_data.csv")
                with open(year_path, "w", encoding="utf-8") as f:
                    f.write(
                        "year,enrolled,housing_capacity,housing_cost_per_student\n"
                        "2021,6000,5200,12000\n"
                        "2022,6300,5200,12500\n"
                        "2023,6700,5400,13000\n"
                        "2024,7100,5400,13500\n"
                        "2025,7600,5400,14000\n"
                    )

                survey_path = os.path.join(tmpdir, "survey_responses.csv")
                with open(survey_path, "w", encoding="utf-8") as f:
                    f.write(
                        "Which dorm are you in?,How would you rate your experience on a scale from 1 to 5?,How does the crowdedness affect your stress level?\n"
                        "single,2,5\n"
                        "double,3,4\n"
                        "triple,2,4\n"
                        "quad,4,3\n"
                        "quint,1,5\n"
                    )

                buf = StringIO()
                with redirect_stdout(buf):
                    exit_code = main.main([year_path, survey_path])

                output = buf.getvalue()

                self.assertEqual(exit_code, 0)
                self.assertIn("=== Survey Outputs ===", output)
                self.assertIn("Stress Level Factor", output)

                self.assertTrue(os.path.exists("summary.txt"))
                with open("summary.txt", "r", encoding="utf-8") as f:
                    text = f.read()
                self.assertIn("Stress Level Factor", text)

            finally:
                os.chdir(old_cwd)


if __name__ == "__main__":
    unittest.main()
