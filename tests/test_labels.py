"""Offline regression tests for discovery, resumable downloads and batch OCR."""

import contextlib
import io
import json
from pathlib import Path
import shutil
import sys
import unittest
from unittest.mock import MagicMock, patch
import urllib.error
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".github" / "scripts"))
import download_ttb_labels as download
import extract_label_text as ocr
import find_new_ttb_labels as discovery
import label_state


class LabelTest(unittest.TestCase):
    def setUp(self):
        self.workspace = Path.cwd() / (".label-test-" + uuid.uuid4().hex)
        self.workspace.mkdir()
        self.addCleanup(shutil.rmtree, self.workspace)

    def legacy(self, ttbid="123", images=("front_label.jpg",), text=False):
        directory = self.workspace / ttbid
        directory.mkdir(exist_ok=True)
        content = "# Label\n\n## Label Images\n\n"
        for name in images:
            (directory / name).write_bytes(b"\xff\xd8\xff" + b"x" * 1000)
            content += f"![Label](./{name})\n"
        if text:
            content += "\n## Extracted Label Text\n\n### Front Label\n\nKentucky straight bourbon whiskey aged seven years\n"
        (directory / "README.md").write_text(content)
        return directory

    def call_main(self, module, arguments):
        with patch.object(sys, "argv", [module.__name__] + arguments), contextlib.redirect_stdout(io.StringIO()):
            return module.main()


class DiscoveryTests(LabelTest):
    def finder(self):
        finder = discovery.TTBLabelFinder()
        self.addCleanup(finder.session.close)
        return finder

    def test_explicit_empty_results(self):
        self.assertEqual(self.finder()._parse_search_results("<html>No records found</html>"), ([], False))

    def test_unrecognized_and_error_pages_fail(self):
        finder = self.finder()
        for content in ("", "<html>Login</html>", "<html>Unable to process request</html>",
                        "<html>CAPTCHA</html>"):
            with self.subTest(content=content), self.assertRaises(ValueError):
                finder._parse_search_results(content)

    def test_nested_table_ids_and_deduplication(self):
        content = '<table><tbody><tr><td><a href="?ttbid=123">X</a></td></tr></tbody></table>'
        self.assertEqual(self.finder()._parse_search_results(content + content), (["123"], False))

    def test_pagination_failure_preserves_ids(self):
        finder = self.finder()
        with patch.object(finder, "_request", return_value=MagicMock(text="ok")), \
                patch.object(finder, "_parse_search_results", return_value=(["123"], True)), \
                patch.object(finder, "_fetch_next_page", side_effect=RuntimeError("page two failed")), \
                patch.object(discovery.time, "sleep"):
            with self.assertRaises(discovery.SearchError) as error:
                finder.search_ttb_registry("01/01/2026", "01/02/2026")
        self.assertEqual(error.exception.partial_ids, ["123"])
        self.assertEqual(error.exception.pages_completed, 1)

    def test_max_pages_is_failure(self):
        finder = self.finder()
        finder.MAX_PAGES = 1
        with patch.object(finder, "_request", return_value=MagicMock(text="ok")), \
                patch.object(finder, "_parse_search_results", return_value=(["123"], True)):
            with self.assertRaisesRegex(discovery.SearchError, "maximum page"):
                finder.search_ttb_registry("01/01/2026", "01/02/2026")

    def test_transient_retries_bounded(self):
        finder = self.finder()
        with patch.object(finder.session, "post", side_effect=discovery.requests.Timeout("timeout")) as post, \
                patch.object(discovery.time, "sleep"):
            with self.assertRaises(discovery.SearchError):
                finder.search_ttb_registry("01/01/2026", "01/02/2026")
        self.assertEqual(post.call_count, 4)

    def test_permanent_http_error_not_retried(self):
        finder = self.finder()
        response = MagicMock(status_code=403)
        error = discovery.requests.HTTPError("forbidden", response=response)
        with patch.object(finder.session, "post", side_effect=error) as post:
            with self.assertRaises(discovery.SearchError):
                finder.search_ttb_registry("01/01/2026", "01/02/2026")
        self.assertEqual(post.call_count, 1)

    def test_pending_local_ids_queued_outside_registry(self):
        self.legacy("100", text=True)
        self.legacy("200", text=False)
        partial = self.legacy("300", images=("front_label.jpg", "back_label.jpg"))
        (partial / "back_label.jpg").unlink()
        (self.workspace / "400").mkdir()
        self.assertEqual(self.finder().work_ids(["100", "500"], self.workspace),
                         ["500", "200", "300", "400"])

    def test_main_json_complete_empty_and_failure(self):
        for error, status, code, partial in (
                (None, "complete", 0, []),
                (discovery.SearchError("network failed"), "failed", 1, []),
                (discovery.SearchError("page two failed", ["123"], 1), "partial", 1, ["123"]),
                (discovery.SearchError("empty first page then failed", [], 1), "partial", 1, [])):
            with self.subTest(status=status, partial=partial):
                output = self.workspace / "result.json"
                with patch.object(discovery.TTBLabelFinder, "search_ttb_registry",
                                  side_effect=error, return_value=[]):
                    self.assertEqual(self.call_main(discovery, [
                        "--labels-dir", str(self.workspace), "--output", str(output)]), code)
                result = json.loads(output.read_text())
                self.assertEqual(result["status"], status)
                self.assertEqual(result["partial_ttb_ids"], partial)
                self.assertEqual(result["partial_count"], len(partial))
                self.assertIn("error", result)


class DownloadTests(LabelTest):
    def attachments(self):
        return [{"filename": "FIRST_FRONT.jpg"}, {"filename": "SECOND_FRONT.jpg"}], {"brand_name": "Example"}

    def test_duplicate_front_names_unique(self):
        names = [item["output_name"] for item in download.image_inventory(self.attachments()[0])]
        self.assertEqual(names, ["front_label.jpg", "front_label_2.jpg"])

    def test_partial_download_retries_only_missing(self):
        def write_first(url, path):
            if path.name == "front_label.jpg":
                path.write_bytes(b"image")
                return True
            return False
        with patch.object(download, "extract_label_images_and_metadata", return_value=self.attachments()), \
                patch.object(download, "download_file", side_effect=write_first):
            self.assertEqual(download.download_ttb_labels("123", self.workspace), "failed")
        directory = self.workspace / "123"
        state = label_state.load_state(directory)
        self.assertEqual(state["download"]["status"], "partial")
        self.assertEqual(len(state["download"]["expected_images"]), 2)
        self.assertEqual(len(state["download"]["downloaded_images"]), 1)

        def write_missing(url, path):
            path.write_bytes(b"second")
            return True
        with patch.object(download, "extract_label_images_and_metadata", return_value=self.attachments()), \
                patch.object(download, "download_file", side_effect=write_missing) as fetch:
            self.assertEqual(download.download_ttb_labels("123", self.workspace), "success")
        self.assertEqual(fetch.call_count, 1)
        self.assertEqual(fetch.call_args.args[1].name, "front_label_2.jpg")
        state = label_state.load_state(directory)
        self.assertTrue(label_state.download_complete(directory, state))
        self.assertEqual(state["ocr"]["status"], "pending")
        with patch.object(download, "extract_label_images_and_metadata") as details:
            self.assertEqual(download.download_ttb_labels("123", self.workspace), "skipped")
            details.assert_not_called()

    def test_legacy_inventory_avoids_redownload_and_pending_ocr(self):
        directory = self.legacy()
        with patch.object(download, "extract_label_images_and_metadata") as details:
            self.assertEqual(download.download_ttb_labels("123", self.workspace), "skipped")
            details.assert_not_called()
        self.assertTrue((directory / label_state.STATE_FILE).exists())
        self.assertFalse(label_state.ocr_complete(directory))

    def test_missing_legacy_inventory_file_retried(self):
        directory = self.legacy(images=("front_label.jpg", "front_label_2.jpg"))
        (directory / "front_label_2.jpg").unlink()
        with patch.object(download, "extract_label_images_and_metadata", return_value=self.attachments()), \
                patch.object(download, "download_file", return_value=False) as fetch:
            self.assertEqual(download.download_ttb_labels("123", self.workspace), "failed")
        self.assertEqual(fetch.call_count, 1)

    def test_empty_download_failure_state(self):
        with patch.object(download, "extract_label_images_and_metadata", return_value=([], {})):
            self.assertEqual(download.download_ttb_labels("123", self.workspace), "failed")
        state = label_state.load_state(self.workspace / "123")
        self.assertEqual(state["download"]["status"], "failed")
        self.assertIn("No label images", state["download"]["error"])

    def test_error_and_captcha_state(self):
        with patch.object(download, "extract_label_images_and_metadata", side_effect=RuntimeError("server failed")):
            self.assertEqual(download.download_ttb_labels("123", self.workspace), "failed")
        self.assertEqual(label_state.load_state(self.workspace / "123")["download"]["error"], "server failed")
        with patch.object(download, "extract_label_images_and_metadata", return_value=("CAPTCHA_DETECTED", {})):
            self.assertEqual(download.download_ttb_labels("123", self.workspace), "captcha")

    def test_nonimage_payload_rejected_without_overwriting(self):
        output = self.workspace / "label.jpg"
        output.write_bytes(b"original")
        with patch.object(download, "fetch_bytes", return_value=b"<html>error" + b"x" * 2000):
            self.assertFalse(download.download_file("https://example.test", output))
        self.assertEqual(output.read_bytes(), b"original")

    def test_retry_bounds_and_permanent_error(self):
        for error, expected in ((TimeoutError("timeout"), 4),
                                (urllib.error.HTTPError("url", 403, "forbidden", {}, None), 1)):
            with self.subTest(error=error), patch.object(download.opener, "open", side_effect=error) as fetch, \
                    patch.object(download.time, "sleep"):
                with self.assertRaises(type(error)):
                    download.fetch_bytes("https://example.test")
                self.assertEqual(fetch.call_count, expected)

    def test_ids_file_and_batch_json(self):
        self.legacy("123")
        ids = self.workspace / "ids.json"
        ids.write_text(json.dumps({"new_ttb_ids": ["123", "456"]}))
        output = self.workspace / "result.json"
        with patch.object(download, "extract_label_images_and_metadata", return_value=([], {})):
            self.assertEqual(self.call_main(download, [
                "--ids-file", str(ids), "--labels-dir", str(self.workspace), "--output", str(output)]), 1)
        result = json.loads(output.read_text())
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["completed_ttb_ids"], ["123"])
        self.assertEqual(result["failed_ttb_ids"], ["456"])


class OCRTests(LabelTest):
    def test_proof_and_abv_units(self):
        for text, expected in (
                ("70 PROOF", "70"), ("PROOF 75", "75"), ("80 PROOF", "80"),
                ("100 PROOF", "100"), ("75% ALC/VOL", "150"),
                ("ALC/VOL 63.55%", "127.1"), ("63.555% ALC/VOL", "127.11"),
                ("60.57% ALC/VOL", "121.14"), ("40%", "80"), ("PROOF | 120.00", "120")):
            with self.subTest(text=text):
                self.assertEqual(ocr.extract_proof_and_age(text)[0], expected)
        self.assertEqual(ocr.extract_proof_and_age("AGED 7 YEARS")[1], "7 Years")

    def test_empty_ocr_fails_and_is_retriable(self):
        directory = self.legacy()
        for value in ("", None, "   "):
            with self.subTest(value=value), patch.object(ocr, "extract_text_from_image", return_value=value):
                self.assertEqual(ocr.process_label_directory(directory), "failed")
            self.assertNotEqual(label_state.load_state(directory)["ocr"]["status"], "complete")
        with patch.object(ocr, "extract_text_from_image", return_value="Kentucky straight bourbon whiskey aged seven years 100 PROOF"):
            self.assertEqual(ocr.process_label_directory(directory), "success")
        self.assertTrue(label_state.ocr_complete(directory))
        with patch.object(ocr, "extract_text_from_image") as extract:
            self.assertEqual(ocr.process_label_directory(directory), "skipped")
            extract.assert_not_called()

    def test_missing_readme_and_images_fail(self):
        directory = self.workspace / "123"
        directory.mkdir()
        self.assertEqual(ocr.process_label_directory(directory), "failed")
        (directory / "README.md").write_text("# Label")
        self.assertEqual(ocr.process_label_directory(directory), "no_images")
        self.assertFalse(label_state.ocr_complete(directory))

    def test_placeholder_section_not_completion(self):
        directory = self.legacy()
        with (directory / "README.md").open("a") as readme:
            readme.write("\n## Extracted Label Text\n\n*No readable text could be extracted from the label images.*\n")
        with patch.object(ocr, "extract_text_from_image", return_value="real text here"):
            self.assertEqual(ocr.process_label_directory(directory), "success")

    def test_partial_ocr_not_complete(self):
        directory = self.legacy(images=("front_label.jpg", "back_label.jpg"))
        with patch.object(ocr, "extract_text_from_image", side_effect=["readable label text", ""]):
            self.assertEqual(ocr.process_label_directory(directory), "failed")
        self.assertEqual(label_state.load_state(directory)["ocr"]["status"], "partial")

    def test_batch_ocr_ids_file(self):
        self.legacy("123")
        self.legacy("456")
        ids = self.workspace / "ids.json"
        ids.write_text(json.dumps({"new_ttb_ids": ["123", "456", "123"]}))
        output = self.workspace / "result.json"
        with patch.object(ocr, "extract_text_from_image", return_value="Kentucky straight bourbon whiskey label text") as extract:
            self.assertEqual(self.call_main(ocr, [
                "--ids-file", str(ids), "--labels-dir", str(self.workspace), "--output", str(output)]), 0)
        self.assertEqual(extract.call_count, 2)
        self.assertEqual(json.loads(output.read_text())["completed_ttb_ids"], ["123", "456"])

    def test_model_cached_once(self):
        fake = MagicMock()
        with patch.dict(sys.modules, {"easyocr": fake}), \
                patch.object(ocr, "_easyocr_reader", None), \
                patch.object(ocr, "_easyocr_unavailable", False):
            first = ocr._get_easyocr_reader()
            self.assertIs(ocr._get_easyocr_reader(), first)
            fake.Reader.assert_called_once()

    def test_batch_missing_and_empty_labels_nonzero(self):
        self.legacy("123")
        ids = self.workspace / "ids.json"
        ids.write_text('{"new_ttb_ids": ["123", "456"]}')
        output = self.workspace / "result.json"
        with patch.object(ocr, "extract_text_from_image", return_value=""):
            self.assertEqual(self.call_main(ocr, [
                "--ids-file", str(ids), "--labels-dir", str(self.workspace), "--output", str(output)]), 1)
        result = json.loads(output.read_text())
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["failed_ttb_ids"], ["123", "456"])
        self.assertIsNotNone(result["error"])


if __name__ == "__main__":
    unittest.main()
