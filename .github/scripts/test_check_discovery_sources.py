import contextlib
from email.message import Message
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import urllib.error

import check_discovery_sources as checker


class SourceHealthTests(unittest.TestCase):
    def response(self, body, content_type="text/html"):
        response = MagicMock()
        response.status = 200
        response.headers = Message()
        response.headers["Content-Type"] = content_type
        response.read.return_value = body.encode()
        response.__enter__.return_value = response
        return response

    def test_prompt_sources(self):
        sources = checker.load_sources(checker.PROMPT.read_text())
        self.assertEqual(len(sources), 6)
        self.assertEqual(sources[0][1], "https://www.breakingbourbon.com/bourbon-rye-whiskey-press-releases")

    def test_healthy_listing(self):
        body = '<p>Bourbon releases</p><a href="/bourbon-whiskey-press-releases/new-release">New release</a>'
        with patch.object(checker.urllib.request, "urlopen", return_value=self.response(body)):
            self.assertIsNone(checker.check_source("Breaking Bourbon", "https://www.breakingbourbon.com/listing"))

    def test_soft_404_and_missing_listings(self):
        for body in (
            "<h1>Not found</h1>",
            '<p>Bourbon</p><a href="/">Home</a>',
            '<script>bourbon</script><a href="/">Home</a>',
        ):
            with self.subTest(body=body):
                self.assertIsNotNone(checker.validate_content("Breaking Bourbon", "https://www.breakingbourbon.com/listing", body))

    def test_generic_source(self):
        self.assertIsNone(checker.validate_content("Other", "https://example.org", '<h1>Whisky news</h1><a href="/review">Review</a>'))

    def test_non_html_and_large_response(self):
        for response in (
            self.response("bourbon", "application/json"),
            self.response("x" * (checker.MAX_BYTES + 1)),
        ):
            with patch.object(checker.urllib.request, "urlopen", return_value=response):
                self.assertIsNotNone(checker.check_source("Source", "https://example.org"))

    def test_permanent_http_failure_not_retried(self):
        for code in (403, 404, 410):
            with self.subTest(code=code), patch.object(checker.urllib.request, "urlopen", side_effect=urllib.error.HTTPError("https://example.org", code, "error", {}, None)) as fetch:
                self.assertEqual(checker.check_source("Source", "https://example.org"), f"HTTP {code}")
                self.assertEqual(fetch.call_count, 1)

    @patch.object(checker.time, "sleep")
    def test_transient_failures_retry_bounded(self, sleep):
        for error in (
            urllib.error.HTTPError("https://example.org", 503, "error", {}, None),
            urllib.error.HTTPError("https://example.org", 429, "error", {}, None),
            urllib.error.URLError("connection refused"),
            TimeoutError("timed out"),
        ):
            with self.subTest(error=error), patch.object(checker.urllib.request, "urlopen", side_effect=error) as fetch:
                self.assertIsNotNone(checker.check_source("Source", "https://example.org"))
                self.assertEqual(fetch.call_count, 4)

    @patch.object(checker.time, "sleep")
    def test_transient_recovery(self, sleep):
        with patch.object(checker.urllib.request, "urlopen", side_effect=[
            TimeoutError(),
            self.response('<p>Rye news</p><a href="/release">Release</a>'),
        ]) as fetch:
            self.assertIsNone(checker.check_source("Source", "https://example.org"))
            self.assertEqual(fetch.call_count, 2)

    def test_run_reports_failure_and_continues(self):
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "report.md"
            with patch.object(checker, "check_source", side_effect=["HTTP 404"] + [None] * 5) as check, contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(checker.run(checker.PROMPT, report), 1)
            self.assertEqual(check.call_count, 6)
            self.assertIn("Checked: 6; failures: 1.", report.read_text())
            self.assertIn("HTTP 404", report.read_text())

    def test_run_success_and_invalid_configuration(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()):
            report = Path(directory) / "report.md"
            with patch.object(checker, "check_source", return_value=None):
                self.assertEqual(checker.run(checker.PROMPT, report), 0)
            prompt = Path(directory) / "empty.md"
            prompt.write_text("No configured sources")
            self.assertEqual(checker.run(prompt, report), 1)
            self.assertIn("Configuration error", report.read_text())


if __name__ == "__main__":
    unittest.main()
