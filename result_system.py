"""Validation, calculation, CSV storage, and class analysis."""

import csv
import math
import re
from pathlib import Path

SUBJECTS = ("Python", "Algorithms", "Network Security", "Database")
PASS_MARK = 40
MAX_MARK = 100
FIELDNAMES = ("registration", *SUBJECTS)


def validate_record(registration, marks):
    registration = registration.strip()
    if not registration:
        raise ValueError("Registration number cannot be blank.")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", registration):
        raise ValueError("Registration number may contain only letters, digits, - and _.")
    if set(marks) != set(SUBJECTS):
        raise ValueError("Enter one mark for each of the four subjects.")
    clean = {}
    for subject in SUBJECTS:
        try:
            value = float(marks[subject])
        except (TypeError, ValueError) as error:
            raise ValueError(f"{subject}: enter a number.") from error
        if not math.isfinite(value) or not 0 <= value <= MAX_MARK:
            raise ValueError(f"{subject}: mark must be from 0 to 100.")
        clean[subject] = value
    return registration, clean


def calculate_result(marks):
    _, clean = validate_record("temporary", marks)
    total = sum(clean.values())
    percentage = total / (len(SUBJECTS) * MAX_MARK) * 100
    if min(clean.values()) < PASS_MARK:
        grade, status = "F", "Fail"
    else:
        status = "Pass"
        grade = next(
            label for threshold, label in
            ((90, "A+"), (80, "A"), (70, "B"), (60, "C"), (40, "D"))
            if percentage >= threshold
        )
    return {"total": total, "percentage": percentage,
            "grade": grade, "status": status}


def class_summary(records):
    if not records:
        return None
    results = {reg: calculate_result(marks) for reg, marks in records.items()}
    count = len(records)
    highest = max(result["total"] for result in results.values())
    return {
        "students": count,
        "class_average": sum(r["percentage"] for r in results.values()) / count,
        "pass_percentage": 100 * sum(r["status"] == "Pass" for r in results.values()) / count,
        "subject_averages": {subject: sum(marks[subject] for marks in records.values()) / count
                             for subject in SUBJECTS},
        "highest_total": highest,
        "highest_students": [reg for reg, result in results.items() if result["total"] == highest],
    }


def load_records(path):
    path = Path(path)
    if not path.exists():
        return {}
    records = {}
    with path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != list(FIELDNAMES):
            raise ValueError("Marks file has an unexpected heading.")
        for row in reader:
            registration, marks = validate_record(
                row["registration"], {subject: row[subject] for subject in SUBJECTS}
            )
            if registration in records:
                raise ValueError(f"Duplicate registration in file: {registration}")
            records[registration] = marks
    return records


def save_records(path, records):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=FIELDNAMES)
        writer.writeheader()
        for registration, marks in records.items():
            writer.writerow({"registration": registration, **marks})


def export_results(path, records):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=("registration", "total", "percentage", "grade", "status"))
        writer.writeheader()
        for registration, marks in records.items():
            result = calculate_result(marks)
            writer.writerow({"registration": registration, "total": f'{result["total"]:.1f}',
                             "percentage": f'{result["percentage"]:.1f}',
                             "grade": result["grade"], "status": result["status"]})
