"""Create the short Colab walkthrough of the result calculation."""

import base64
import contextlib
import io
import json
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Student_Result_System_Working.ipynb"

STEPS = [
    ("### 1. Calculate one result\nEach subject is out of 100. A student needs at least 40 in every subject to pass.", '''SUBJECTS = ("Python", "Algorithms", "Network Security", "Database")

def calculate_result(marks):
    for subject in SUBJECTS:
        if not 0 <= marks[subject] <= 100:
            raise ValueError(f"{subject} must be between 0 and 100")

    total = sum(marks.values())
    percentage = total / 4

    if any(mark < 40 for mark in marks.values()):
        return total, percentage, "F", "Fail"

    if percentage >= 90:
        grade = "A+"
    elif percentage >= 80:
        grade = "A"
    elif percentage >= 70:
        grade = "B"
    elif percentage >= 60:
        grade = "C"
    else:
        grade = "D"
    return total, percentage, grade, "Pass"

print("Result function is ready.")
'''),
    ("### 2. Enter three example students\nThese marks are illustrative and are not official academic records.", '''students = {
    "AP26122050024": {"Python": 82, "Algorithms": 76, "Network Security": 91, "Database": 65},
    "DEMO_A": {"Python": 92, "Algorithms": 88, "Network Security": 94, "Database": 90},
    "DEMO_B": {"Python": 78, "Algorithms": 72, "Network Security": 35, "Database": 85},
}

print("Example students:", len(students))
'''),
    ("### 3. Show each result\nThe total, percentage, grade, and pass/fail status come from the same function.", '''results = {}
for registration, marks in students.items():
    results[registration] = calculate_result(marks)
    total, percentage, grade, status = results[registration]
    print(f"{registration}: {total}/400 | {percentage:.1f}% | {grade} | {status}")
'''),
    ("### 4. Compare the class\nSort by percentage, then calculate the class average and pass rate. A percentage alone does not decide pass/fail.", '''ranked = sorted(results.items(), key=lambda item: item[1][1], reverse=True)

print("Ranking:")
for position, (registration, result) in enumerate(ranked, start=1):
    print(f"{position}. {registration}: {result[1]:.1f}% ({result[3]})")

class_average = sum(result[1] for result in results.values()) / len(results)
pass_rate = sum(result[3] == "Pass" for result in results.values()) / len(results) * 100
print(f"Class average: {class_average:.1f}%")
print(f"Pass rate: {pass_rate:.1f}%")
print("DEMO_B fails because Network Security is 35, below 40.")
'''),
    ("### 5. Draw the comparison chart\nThe bars show percentages; gray marks the student who failed a subject.", '''import matplotlib.pyplot as plt

names = [registration for registration, result in ranked]
percentages = [result[1] for registration, result in ranked]
colors = ["#C8102E" if result[3] == "Pass" else "#777777" for registration, result in ranked]

plt.figure(figsize=(8, 4))
bars = plt.bar(names, percentages, color=colors)
plt.bar_label(bars, fmt="%.1f%%")
plt.ylim(0, 100)
plt.ylabel("Percentage")
plt.title("Student result comparison")
plt.tight_layout()
plt.show()
'''),
    ("### 6. Save the report\nThe website's **Export CSV** button saves the same result fields.", '''import csv

with open("student_results.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Registration", "Total", "Percentage", "Grade", "Status"])
    for registration, result in results.items():
        writer.writerow([registration, result[0], f"{result[1]:.1f}", result[2], result[3]])

with open("student_results.csv", encoding="utf-8") as file:
    print(file.read())
'''),
]

EXPLANATIONS = [
    """**What this code does**

- `SUBJECTS` lists the four subjects. Each mark must be between 0 and 100; otherwise the function shows an error.
- `sum(marks.values())` adds the four marks. Dividing by `4` gives the percentage because each subject is out of 100.
- `any(mark < 40 ...)` checks whether even one subject is below 40. If so, the function returns **F, Fail** immediately.
- If every subject passes, the `if`/`elif` statements choose the grade from the percentage. `return` sends back total, percentage, grade, and status.

**Example:** marks of 82, 76, 91, and 65 give 314/400, or 78.5%, which is B and Pass.""",
    """**What this code does**

- `students` is a dictionary. Each registration number points to another dictionary of four subject marks.
- `DEMO_A` and `DEMO_B` are made-up records for showing two different outcomes.
- `len(students)` counts how many example students were entered.

Change these marks to try your own examples, keeping each mark between 0 and 100.""",
    """**What this code does**

- The `for` loop takes one registration number and its marks at a time.
- `calculate_result(marks)` applies the same grading rules to each student.
- The four values returned by the function are put into `total`, `percentage`, `grade`, and `status`.
- The `print` line displays one complete result. `:.1f` shows the percentage with one digit after the decimal point.""",
    """**What this code does**

- `sorted(..., reverse=True)` puts the highest percentage first. In `item[1][1]`, the first `[1]` selects the result tuple and the second `[1]` selects its percentage.
- `enumerate(..., start=1)` adds ranking numbers 1, 2, and 3.
- The class average is the mean of the three percentages. The pass rate counts the students with status `Pass`, divides by the number of students, and multiplies by 100.
- `DEMO_B` still fails at 67.5% overall because its Network Security mark is 35, below the required 40.""",
    """**What this code does**

- `matplotlib.pyplot` draws the chart. `names` and `percentages` supply the labels and bar heights.
- Passing students get red bars; a student who failed gets a gray bar.
- `bar_label` writes each percentage above its bar. `ylim(0, 100)` keeps the scale from 0 to 100.
- `tight_layout()` makes the labels fit, and `show()` displays the chart.""",
    """**What this code does**

- `csv.writer` creates a CSV report that a spreadsheet can open.
- The first `writerow` writes the column headings. The loop writes one result row per student.
- Opening the file with `newline=""` prevents extra blank lines in CSV files on Windows.
- The last `with open(...)` reads the saved file so you can see what was written. Each `with` closes its file automatically.""",
]


def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source}


def code_cell(source, count, outputs):
    return {"cell_type": "code", "metadata": {}, "source": source,
            "execution_count": count, "outputs": outputs}


def build():
    cells = [md("# Student Academic Result Analysis System\n"
                "## How the project works\n\n"
                "**Registration:** AP26122050024  \n"
                "This notebook explains only the result calculation and comparison. "
                "The desktop and website interfaces use the same grading rules.")]
    scope = {}
    with tempfile.TemporaryDirectory() as folder:
        import os
        previous = os.getcwd()
        os.chdir(folder)
        try:
            for number, (description, source) in enumerate(STEPS, start=1):
                cells.append(md(description))
                stream = io.StringIO()
                with contextlib.redirect_stdout(stream):
                    exec(source, scope)
                outputs = []
                if stream.getvalue():
                    outputs.append({"output_type": "stream", "name": "stdout", "text": stream.getvalue()})
                if number == 5:
                    image = io.BytesIO()
                    plt.gcf().savefig(image, format="png", dpi=140)
                    outputs.append({"output_type": "display_data", "metadata": {},
                                    "data": {"image/png": base64.b64encode(image.getvalue()).decode("ascii")}})
                    plt.close("all")
                cells.append(code_cell(source, number, outputs))
                cells.append(md(EXPLANATIONS[number - 1]))
        finally:
            os.chdir(previous)
    notebook = {"nbformat": 4, "nbformat_minor": 4, "cells": cells,
                "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                             "language_info": {"name": "python"}}}
    OUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    build()
