# Student Academic Result Analysis System

A small Python terminal project for recording marks, calculating results, checking errors, viewing class summaries, drawing a subject chart, and exporting a CSV report.

## Explain it in class

“First I enter a registration number and four subject marks. The program checks that every mark is between 0 and 100. It adds the marks and calculates the percentage. If any subject is below 40, the student fails; otherwise it chooses a grade. It can also show class averages, draw a chart, and save the results.”

The main code to explain is `calculate_result()` in `result_system.py`. `main.py` only shows the menu and asks the user what to do. The CSV functions save and reopen records.

## Run

Requires Python 3.10 or newer. In PowerShell:

```powershell
cd "path\to\student-academic-result-analysis"
python -m pip install -r requirements.txt
python main.py
```

`matplotlib` is needed only for the chart. All other options use Python's standard library. The program creates `data/marks.csv` when a student is added and `data/results.csv` when results are exported. These files stay on your computer.

## Example for a class demonstration

Enter registration `AP26122050024` and the **illustrative** marks: Python 82, Algorithms 76, Network Security 91, Database 65. The displayed result is 314/400, 78.5%, B, Pass. These are sample marks, not an academic record.

Try 105 as one mark to show the validation message. Add a second student, then choose Class summary to show the averages and pass percentage. Choose Show chart to save a PNG under `data/`.

## Example grading rules

Each of the four subjects is out of 100. Passing requires at least 40 in **every** subject. If a subject is below 40, the result is F/Fail even when the overall percentage is high. Otherwise, the percentage bands are 90+ A+, 80+ A, 70+ B, 60+ C, and 40+ D. These are configurable project examples, **not official university rules**.

## Files

- `main.py`: interactive terminal menu and chart.
- `result_system.py`: validation, calculations, class analysis, and CSV storage.
- `tests/test_result_system.py`: normal, boundary, failure, and file tests.
- `requirements.txt`: chart dependency.

Run tests with `python -m unittest discover -s tests -v`.
