"""Run the Student Academic Result Analysis System in a terminal."""

from pathlib import Path
from result_system import (SUBJECTS, calculate_result, class_summary,
                           export_results, load_records, save_records, validate_record)

DATA_FILE = Path("data/marks.csv")
REPORT_FILE = Path("data/results.csv")


def print_result(registration, marks):
    result = calculate_result(marks)
    print(f"\nRegistration: {registration}")
    for subject in SUBJECTS:
        print(f"  {subject}: {marks[subject]:g}/100")
    print(f'Total: {result["total"]:g}/400')
    print(f'Percentage: {result["percentage"]:.1f}%')
    print(f'Grade: {result["grade"]} | Status: {result["status"]}')


def plot_marks(registration, marks):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Install matplotlib first: python -m pip install -r requirements.txt")
        return
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(SUBJECTS, [marks[s] for s in SUBJECTS], color="#C8102E")
    ax.bar_label(bars, fmt="%.0f")
    ax.set_ylim(0, 100)
    ax.set_ylabel("Marks out of 100")
    ax.set_title(f"Subject marks: {registration}")
    fig.tight_layout()
    chart_path = Path("data") / f"chart_{registration}.png"
    fig.savefig(chart_path, dpi=160)
    print(f"Chart saved to {chart_path}")
    plt.show()


def main():
    try:
        records = load_records(DATA_FILE)
    except (OSError, ValueError) as error:
        print(f"Cannot read marks file: {error}")
        return
    while True:
        print("\nSTUDENT ACADEMIC RESULT ANALYSIS SYSTEM")
        print("1 Add student  2 View result  3 Class summary")
        print("4 Show chart  5 Export results  6 List students  0 Exit")
        choice = input("Choose: ").strip()
        if choice == "0":
            print("Goodbye.")
            return
        if choice == "1":
            registration = input("Registration number: ").strip()
            if registration in records:
                print("Error: this registration number is already present.")
                continue
            entered = {subject: input(f"{subject} mark (0-100): ") for subject in SUBJECTS}
            try:
                registration, marks = validate_record(registration, entered)
                records[registration] = marks
                save_records(DATA_FILE, records)
                print("Student saved.")
                print_result(registration, marks)
            except (ValueError, OSError) as error:
                records.pop(registration, None)
                print(f"Error: {error}")
        elif choice in ("2", "4"):
            registration = input("Registration number: ").strip()
            if registration not in records:
                print("Error: student not found.")
            elif choice == "2":
                print_result(registration, records[registration])
            else:
                plot_marks(registration, records[registration])
        elif choice == "3":
            summary = class_summary(records)
            if summary is None:
                print("No results available.")
                continue
            print(f'Students: {summary["students"]}')
            print(f'Class average: {summary["class_average"]:.1f}%')
            print(f'Pass percentage: {summary["pass_percentage"]:.1f}%')
            for subject, average in summary["subject_averages"].items():
                print(f"{subject} average: {average:.1f}")
            print(f'Highest total: {summary["highest_total"]:g}/400')
            print("Highest student(s): " + ", ".join(summary["highest_students"]))
        elif choice == "5":
            try:
                export_results(REPORT_FILE, records)
                print(f"Report saved to {REPORT_FILE}")
            except OSError as error:
                print(f"Could not save the report: {error}")
        elif choice == "6":
            print("\n".join(records) if records else "No students registered.")
        else:
            print("Choose a number from the menu.")


if __name__ == "__main__":
    main()
