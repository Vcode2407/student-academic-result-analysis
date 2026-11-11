"""Check the local website against temporary student files."""

import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import web_app


class WebsiteTests(unittest.TestCase):
    def test_add_validate_analyse_and_export(self):
        with tempfile.TemporaryDirectory() as folder:
            old_marks, old_report = web_app.MARKS_FILE, web_app.REPORT_FILE
            web_app.MARKS_FILE = Path(folder) / "marks.csv"
            web_app.REPORT_FILE = Path(folder) / "results.csv"
            server = ThreadingHTTPServer(("127.0.0.1", 0), web_app.Handler)
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            base = f"http://127.0.0.1:{server.server_port}"

            def post(marks):
                data = json.dumps({"registration": "TEST01", "marks": marks}).encode()
                request = Request(base + "/api/records", data=data,
                                  headers={"Content-Type": "application/json"})
                return urlopen(request)

            try:
                marks = {"Python": 82, "Algorithms": 76,
                         "Network Security": 91, "Database": 65}
                with post(marks) as response:
                    self.assertEqual(response.status, 201)
                    self.assertEqual(json.load(response)["result"]["grade"], "B")
                with urlopen(base + "/api/summary") as response:
                    self.assertEqual(json.load(response)["class_average"], 78.5)
                with urlopen(base + "/api/report") as response:
                    self.assertIn(b"TEST01,314.0,78.5,B,Pass", response.read())
                for invalid in (marks, {**marks, "Python": 105}):
                    with self.assertRaises(HTTPError) as error:
                        post(invalid)
                    self.assertEqual(error.exception.code, 400)
                with urlopen(base + "/api/records") as response:
                    self.assertEqual(len(json.load(response)), 1)
            finally:
                server.shutdown()
                server.server_close()
                worker.join()
                web_app.MARKS_FILE, web_app.REPORT_FILE = old_marks, old_report


if __name__ == "__main__":
    unittest.main()
