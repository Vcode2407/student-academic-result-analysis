"""Validation, calculation, CSV storage, and class analysis."""

import csv
import math
from pathlib import Path

SUBJECTS = ("Python", "Algorithms", "Network Security", "Database")
PASS_MARK = 40
MAX_MARK = 100
FIELDNAMES = ("registration", *SUBJECTS)


def validate_record(registration, marks):
    registration = registration.strip()
    if not registration:
        raise ValueError("Registration number cannot be blank.")
    if not all(character.isalnum() or character in "-_" for character in registration):
        raise ValueError("Registration number may contain only letters, digits, - and _.")
    return registration, validate_marks(marks)


def validate_marks(marks):
    """Check all four marks before using them in a result."""
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
    return clean


def calculate_result(marks):
    """Turn one student's marks into a total, percentage, and grade."""
    clean = validate_marks(marks)
    total = sum(clean.values())
    percentage = total / 400 * 100
    if min(clean.values()) < PASS_MARK:
        grade, status = "F", "Fail"
    else:
        # Check the highest grade first, just like the presentation shows.
        for limit, label in [(90, "A+"), (80, "A"), (70, "B"),
                             (60, "C"), (40, "D")]:
            if percentage >= limit:
                grade, status = label, "Pass"
                break
    return {"total": total, "percentage": percentage,
            "grade": grade, "status": status}


def class_summary(records):
    """Find averages, pass percentage, and the highest result in a class."""
    if not records:
        return None
    count = len(records)
    results = {registration: calculate_result(marks)
               for registration, marks in records.items()}
    highest = max(result["total"] for result in results.values())
    passed = sum(result["status"] == "Pass" for result in results.values())
    subject_averages = {}
    for subject in SUBJECTS:
        subject_total = sum(marks[subject] for marks in records.values())
        subject_averages[subject] = subject_total / count
    return {
        "students": count,
        "class_average": sum(result["percentage"] for result in results.values()) / count,
        "pass_percentage": passed / count * 100,
        "subject_averages": subject_averages,
        "highest_total": highest,
        "highest_students": [registration for registration, result in results.items()
                             if result["total"] == highest],
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
