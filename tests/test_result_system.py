import tempfile
import unittest
from pathlib import Path

from result_system import (SUBJECTS, calculate_result, class_summary,
                           export_results, load_records, save_records, validate_record)


def marks(*values):
    return dict(zip(SUBJECTS, values))


class ResultSystemTests(unittest.TestCase):
    def test_sample_result(self):
        self.assertEqual(calculate_result(marks(82, 76, 91, 65)),
                         {"total": 314.0, "percentage": 78.5, "grade": "B", "status": "Pass"})

    def test_boundary_pass(self):
        self.assertEqual(calculate_result(marks(40, 40, 40, 40))["grade"], "D")

    def test_one_failed_subject_overrides_average(self):
        result = calculate_result(marks(90, 88, 35, 95))
        self.assertEqual((result["percentage"], result["grade"], result["status"]),
                         (77.0, "F", "Fail"))

    def test_invalid_marks(self):
        for bad in (-5, 105, "abc", "nan", "inf"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                validate_record("R1", marks(bad, 50, 50, 50))

    def test_empty_class(self):
        self.assertIsNone(class_summary({}))

    def test_invalid_registration(self):
        with self.assertRaises(ValueError):
            validate_record("../other", marks(50, 50, 50, 50))

    def test_summary_and_csv_round_trip(self):
        records = {"R1": marks(82, 76, 91, 65), "R2": marks(40, 40, 40, 40)}
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "marks.csv"
            report = Path(folder) / "results.csv"
            save_records(source, records)
            loaded = load_records(source)
            export_results(report, loaded)
            self.assertEqual(loaded, records)
            self.assertEqual(class_summary(loaded)["pass_percentage"], 100.0)
            self.assertIn("R1,314.0,78.5,B,Pass", report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
