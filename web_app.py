"""Local website for the Student Academic Result Analysis System."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from result_system import (SUBJECTS, calculate_result, class_summary,
                           export_results, load_records, save_records, validate_record)

ROOT = Path(__file__).parent
MARKS_FILE = ROOT / "data" / "marks.csv"
REPORT_FILE = ROOT / "data" / "results.csv"
WEB = ROOT / "web"
ASSETS = {"/": ("index.html", "text/html"),
          "/styles.css": ("styles.css", "text/css"),
          "/app.js": ("app.js", "text/javascript")}


def record_list(records):
    return [{"registration": number, "marks": marks,
             "result": calculate_result(marks)} for number, marks in records.items()]


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Keep the server usable when launched without a console window."""
        pass

    def send_data(self, data, status=200, content_type="application/json"):
        body = json.dumps(data).encode("utf-8") if content_type == "application/json" else data
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        try:
            if path in ASSETS:
                filename, content_type = ASSETS[path]
                self.send_data((WEB / filename).read_bytes(), content_type=content_type)
            elif path == "/api/records":
                self.send_data(record_list(load_records(MARKS_FILE)))
            elif path == "/api/summary":
                self.send_data(class_summary(load_records(MARKS_FILE)))
            elif path == "/api/report":
                export_results(REPORT_FILE, load_records(MARKS_FILE))
                body = REPORT_FILE.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Disposition", 'attachment; filename="student_results.csv"')
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_data({"error": "Page not found."}, 404)
        except (OSError, ValueError) as error:
            self.send_data({"error": str(error)}, 500)

    def do_POST(self):
        if urlparse(self.path).path != "/api/records":
            self.send_data({"error": "Page not found."}, 404)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 10000:
                raise ValueError("Invalid request size.")
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict) or not isinstance(data.get("marks"), dict):
                raise ValueError("Enter a registration number and four marks.")
            number, marks = validate_record(data.get("registration", ""), data["marks"])
            records = load_records(MARKS_FILE)
            if number in records:
                raise ValueError("This registration number is already saved.")
            records[number] = marks
            save_records(MARKS_FILE, records)
            self.send_data({"registration": number, "marks": marks,
                            "result": calculate_result(marks)}, 201)
        except (ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
            self.send_data({"error": str(error)}, 400)
        except OSError as error:
            self.send_data({"error": str(error)}, 500)


if __name__ == "__main__":
    address = ("127.0.0.1", 8765)
    print(f"Open http://{address[0]}:{address[1]}/", flush=True)
    ThreadingHTTPServer(address, Handler).serve_forever()
