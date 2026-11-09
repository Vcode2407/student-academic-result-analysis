"""A simple window for entering marks and showing results."""

import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path

from result_system import (SUBJECTS, calculate_result, class_summary,
                           export_results, load_records, save_records, validate_record)

DATA = Path(__file__).parent / "data"
MARKS_FILE = DATA / "marks.csv"
REPORT_FILE = DATA / "results.csv"
RED = "#C8102E"
BLACK = "#171717"


class ResultApp:
    def __init__(self, window):
        self.window = window
        window.title("Student Academic Result Analysis System")
        window.geometry("1100x700")
        window.configure(bg="white")
        try:
            self.records = load_records(MARKS_FILE)
        except (OSError, ValueError) as error:
            messagebox.showerror("File error", str(error))
            self.records = {}

        tk.Label(window, text="STUDENT ACADEMIC RESULT ANALYSIS SYSTEM",
                 bg=BLACK, fg="white", font=("Segoe UI", 21, "bold"),
                 pady=20).pack(fill="x")
        tk.Label(window, text="Enter marks • View result • Analyse class • Save report",
                 bg="white", fg=RED, font=("Segoe UI", 12)).pack(pady=12)

        body = tk.Frame(window, bg="white")
        body.pack(fill="both", expand=True, padx=28)
        form = tk.Frame(body, bg="white")
        form.pack(side="left", anchor="n", padx=(0, 45))
        tk.Label(form, text="Student details", bg="white", fg=BLACK,
                 font=("Segoe UI", 17, "bold")).pack(anchor="w", pady=(8, 16))

        self.registration = self.entry(form, "Registration number")
        self.marks = {subject: self.entry(form, f"{subject} (0–100)")
                      for subject in SUBJECTS}
        tk.Button(form, text="Add student", command=self.add_student,
                  bg=RED, fg="white", font=("Segoe UI", 11, "bold"),
                  width=25, pady=8).pack(pady=18)

        right = tk.Frame(body, bg="white")
        right.pack(side="left", fill="both", expand=True)
        tk.Label(right, text="Saved students", bg="white", fg=BLACK,
                 font=("Segoe UI", 17, "bold")).pack(anchor="w", pady=(8, 10))
        columns = ("Registration", "Total", "Percentage", "Grade", "Status")
        self.table = ttk.Treeview(right, columns=columns, show="headings", height=8)
        for column in columns:
            self.table.heading(column, text=column)
            self.table.column(column, width=135, anchor="center")
        self.table.pack(fill="x")
        self.table.bind("<<TreeviewSelect>>", self.show_result)

        buttons = tk.Frame(right, bg="white")
        buttons.pack(anchor="w", pady=16)
        for label, action in (("Class summary", self.show_summary),
                              ("Subject chart", self.show_chart),
                              ("Save CSV report", self.save_report)):
            tk.Button(buttons, text=label, command=action, bg=BLACK, fg="white",
                      font=("Segoe UI", 10), padx=12, pady=7).pack(side="left", padx=(0, 9))
        self.output = tk.StringVar(value="Select a student to view the result.")
        tk.Label(right, textvariable=self.output, justify="left", anchor="nw",
                 bg="#F4F4F4", fg=BLACK, font=("Segoe UI", 12),
                 padx=18, pady=18, width=55, height=9).pack(fill="both", expand=True)
        tk.Label(window, text="Sample project rules: 40 in every subject to pass. Grades are examples.",
                 bg="white", fg="#555555", font=("Segoe UI", 10)).pack(pady=13)
        self.refresh_table()

    def entry(self, parent, label):
        tk.Label(parent, text=label, bg="white", fg=BLACK,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(7, 3))
        box = tk.Entry(parent, font=("Segoe UI", 12), width=26)
        box.pack(anchor="w")
        return box

    def refresh_table(self):
        for item in self.table.get_children():
            self.table.delete(item)
        for registration, marks in self.records.items():
            result = calculate_result(marks)
            self.table.insert("", "end", iid=registration,
                              values=(registration, f'{result["total"]:g}',
                                      f'{result["percentage"]:.1f}%',
                                      result["grade"], result["status"]))

    def add_student(self):
        try:
            registration, marks = validate_record(
                self.registration.get(),
                {subject: box.get() for subject, box in self.marks.items()})
            if registration in self.records:
                raise ValueError("This registration number is already saved.")
            self.records[registration] = marks
            try:
                save_records(MARKS_FILE, self.records)
            except OSError:
                del self.records[registration]
                raise
        except (ValueError, OSError) as error:
            messagebox.showerror("Cannot add student", str(error))
            return
        self.refresh_table()
        self.table.selection_set(registration)
        self.table.see(registration)
        self.show_result()

    def selected_student(self):
        selection = self.table.selection()
        if not selection:
            messagebox.showinfo("Select a student", "Select a row in the table first.")
            return None
        return selection[0]

    def show_result(self, _event=None):
        selection = self.table.selection()
        if not selection:
            return
        registration = selection[0]
        result = calculate_result(self.records[registration])
        self.output.set(f'Registration: {registration}\n'
                        f'Total: {result["total"]:g} / 400\n'
                        f'Percentage: {result["percentage"]:.1f}%\n'
                        f'Grade: {result["grade"]}\n'
                        f'Status: {result["status"]}')

    def show_summary(self):
        summary = class_summary(self.records)
        if summary is None:
            self.output.set("No results available.")
            return
        lines = [f'Students: {summary["students"]}',
                 f'Class average: {summary["class_average"]:.1f}%',
                 f'Pass percentage: {summary["pass_percentage"]:.1f}%']
        for subject, average in summary["subject_averages"].items():
            lines.append(f'{subject} average: {average:.1f}')
        lines.append(f'Highest total: {summary["highest_total"]:g} / 400')
        self.output.set("\n".join(lines))

    def show_chart(self):
        registration = self.selected_student()
        if registration is None:
            return
        try:
            from main import plot_marks
            plot_marks(registration, self.records[registration])
        except (OSError, ValueError) as error:
            messagebox.showerror("Chart error", str(error))

    def save_report(self):
        try:
            export_results(REPORT_FILE, self.records)
            messagebox.showinfo("Report saved", f"Saved to:\n{REPORT_FILE}")
        except OSError as error:
            messagebox.showerror("File error", str(error))


if __name__ == "__main__":
    root = tk.Tk()
    ResultApp(root)
    root.mainloop()
