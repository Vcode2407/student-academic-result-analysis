# Student Academic Result Analysis System

A small Python project with a local website, desktop interface, and terminal menu for recording marks, calculating results, viewing class analysis, drawing charts, and exporting a CSV report.

## Explain it in class

“First I enter a registration number and four subject marks. The program checks that every mark is between 0 and 100. It adds the marks and calculates the percentage. If any subject is below 40, the student fails; otherwise it chooses a grade. It can also show class averages, draw a chart, and save the results.”

For a short, runnable explanation of the calculation and comparison, open
[`Student_Result_System_Working.ipynb`](Student_Result_System_Working.ipynb) in
Jupyter or Google Colab. It includes example output and a comparison chart.

The main code to explain is `calculate_result()` in `result_system.py`. `main.py` only shows the menu and asks the user what to do. The CSV functions save and reopen records.

## Run

Requires Python 3.10 or newer. In PowerShell:

```powershell
cd "path\to\student-academic-result-analysis"
python -m pip install -r requirements.txt
python main.py
```

For the desktop interface, run `python gui.py` instead. Enter the registration
number and four marks, click **Add student**, then select the saved row to see its
result. The **Class summary**, **Subject chart**, and **Save CSV report** buttons
show the other features. The saved report is `data/results.csv`.

For the local website, run `python web_app.py` from the project folder and open
<http://127.0.0.1:8765/> in a browser. The website uses the same `data/marks.csv`
records as the desktop program. Select a student to see the subject chart, or
click **Export CSV** to download the results. The class analysis section shows
subject averages and the highest total. Keep the terminal open while using
the website. This localhost address works on your computer only.

The **Compare students** section ranks saved results by percentage and still
shows the pass/fail decision. Two illustrative records demonstrate different
outcomes: `DEMO_A` has marks 92, 88, 94, 90 (91.0%, A+, Pass), while `DEMO_B`
has 78, 72, 35, 85 (67.5%, F, Fail because Network Security is below 40).
These demo marks are not real student records.

`matplotlib` is needed only for the chart. All other options use Python's standard library. The program creates `data/marks.csv` when a student is added and `data/results.csv` when results are exported. These files stay on your computer.

## Example for a class demonstration

Enter registration `AP26122050024` and the **illustrative** marks: Python 82, Algorithms 76, Network Security 91, Database 65. The displayed result is 314/400, 78.5%, B, Pass. These are sample marks, not an academic record.

Try 105 as one mark to show the validation message. Add a second student, then choose **Class summary** to show the averages and pass percentage. Choose **Subject chart** to show a chart and save a PNG under `data/`.

## Interface screenshots

The sample marks shown here are illustrative. Click any image to view it at full size.

- [Student entry and saved records](screenshots/01_interface.jpg)
- [Individual result](screenshots/02_result.jpg)
- [Class summary](screenshots/03_class_summary.jpg)
- [Subject chart](screenshots/04_subject_chart.jpg)
- [Local website](screenshots/05_local_website.png)
- [Local website on a phone-sized screen](screenshots/06_local_website_mobile.png)
- [Three-student comparison](screenshots/07_comparison.png)
- [Failed-subject example](screenshots/08_failed_subject.png)

## Example grading rules

Each of the four subjects is out of 100. Passing requires at least 40 in **every** subject. If a subject is below 40, the result is F/Fail even when the overall percentage is high. Otherwise, the percentage bands are 90+ A+, 80+ A, 70+ B, 60+ C, and 40+ D. These are configurable project examples, **not official university rules**.

## Files

- `main.py`: interactive terminal menu and chart.
- `gui.py`: desktop interface for the same project.
- `web_app.py` and `web/`: local website and its browser files.
- `result_system.py`: validation, calculations, class analysis, and CSV storage.
- `tests/test_result_system.py`: normal, boundary, failure, and file tests.
- `requirements.txt`: chart dependency.
- `screenshots/`: demonstration images of the desktop interface and website.

Run tests with `python -m unittest discover -s tests -v`.
