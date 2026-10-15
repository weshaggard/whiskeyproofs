"""Offline URL-validator tests; run with python3 -m unittest discover -s tests."""

import csv
import importlib.util
import io
import json
from pathlib import Path
import socket
import ssl
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import urllib.error


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'validate_urls', ROOT / '.github/scripts/validate_urls.py'
)
urls = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(urls)


def response(status=200):
    result = MagicMock()
    result.__enter__.return_value = result
    result.status = status
    return result


class NetworkTests(unittest.TestCase):
    def setUp(self):
        self.sleep = patch.object(urls.time, 'sleep').start()
        self.addCleanup(patch.stopall)

    def test_success_closes_response_and_uses_verified_default_context(self):
        reply = response()
        with patch.object(urls.urllib.request, 'urlopen', return_value=reply) as request:
            self.assertEqual(urls.validate_url('https://example.com'), (True, '', False))
        reply.__exit__.assert_called_once()
        self.assertEqual(request.call_args.kwargs, {'timeout': 10})

    def test_head_unsupported_falls_back_and_closes_http_error(self):
        for code in (405, 501):
            with self.subTest(code=code):
                body = io.BytesIO()
                error = urllib.error.HTTPError('https://example.com', code, '', {}, body)
                reply = response()
                with patch.object(urls.urllib.request, 'urlopen',
                                  side_effect=[error, reply]) as request:
                    self.assertTrue(urls.validate_url('https://example.com')[0])
                self.assertEqual([call.args[0].method for call in request.call_args_list],
                                 ['HEAD', 'GET'])
                self.assertTrue(body.closed)
                reply.__exit__.assert_called_once()

    def test_unraised_unsupported_status_also_falls_back(self):
        head = response(405)
        with patch.object(urls.urllib.request, 'urlopen',
                          side_effect=[head, response()]) as request:
            self.assertTrue(urls.validate_url('https://example.com')[0])
        self.assertEqual(request.call_count, 2)
        head.__exit__.assert_called_once()

    def test_dns_temporary_and_nonexistent(self):
        for errno, transient, attempts in ((socket.EAI_AGAIN, True, 3),
                                            (socket.EAI_NONAME, False, 1)):
            with self.subTest(errno=errno):
                error = urllib.error.URLError(socket.gaierror(errno, 'DNS failed'))
                with patch.object(urls.urllib.request, 'urlopen', side_effect=error) as request:
                    valid, message, actual = urls.validate_url('https://example.com')
                self.assertFalse(valid)
                self.assertIn('DNS Error', message)
                self.assertEqual(actual, transient)
                self.assertEqual(request.call_count, attempts)

    def test_retries_recover(self):
        with patch.object(urls.urllib.request, 'urlopen',
                          side_effect=[TimeoutError('timeout'), response()]) as request:
            self.assertTrue(urls.validate_url('https://example.com')[0])
        self.assertEqual(request.call_count, 2)
        self.sleep.assert_called_once()

    def test_tls_remains_unknown_with_no_insecure_retry(self):
        for error in (ssl.SSLCertVerificationError('bad certificate'),
                      urllib.error.URLError(ssl.SSLError('TLS failure'))):
            with self.subTest(error=error):
                with patch.object(urls.urllib.request, 'urlopen', side_effect=error) as request:
                    valid, message, transient = urls.validate_url('https://example.com')
                self.assertFalse(valid)
                self.assertTrue(transient)
                self.assertIn('TLS Error', message)
                self.assertEqual(request.call_count, 3)
                self.assertTrue(all('context' not in call.kwargs
                                    for call in request.call_args_list))

    def test_http_classification_and_bounded_retries(self):
        for code, transient, attempts in ((403, True, 3), (429, True, 3),
                                          (503, True, 3), (404, False, 1),
                                          (410, False, 1)):
            with self.subTest(code=code):
                bodies = [io.BytesIO() for _ in range(attempts)]
                errors = [urllib.error.HTTPError('https://example.com', code, '', {}, body)
                          for body in bodies]
                with patch.object(urls.urllib.request, 'urlopen', side_effect=errors) as request:
                    self.assertEqual(urls.validate_url('https://example.com'),
                                     (False, f'HTTP {code}', transient))
                self.assertEqual(request.call_count, attempts)
                self.assertTrue(all(body.closed for body in bodies))

    def test_fallback_get_definitive_error_is_not_retried(self):
        errors = [urllib.error.HTTPError('https://example.com', code, '', {}, io.BytesIO())
                  for code in (405, 404)]
        with patch.object(urls.urllib.request, 'urlopen', side_effect=errors) as request:
            self.assertEqual(urls.validate_url('https://example.com'),
                             (False, 'HTTP 404', False))
        self.assertEqual(request.call_count, 2)

    def test_fallback_get_transient_errors_have_bounded_retries(self):
        errors = [urllib.error.HTTPError('https://example.com', code, '', {}, io.BytesIO())
                  for code in (405, 503, 405, 503, 405, 503)]
        with patch.object(urls.urllib.request, 'urlopen', side_effect=errors) as request:
            self.assertEqual(urls.validate_url('https://example.com'),
                             (False, 'HTTP 503', True))
        self.assertEqual(request.call_count, 6)
        self.assertEqual(self.sleep.call_count, 2)


class CsvTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=ROOT)
        self.addCleanup(self.directory.cleanup)
        self.csv = Path(self.directory.name) / 'index.csv'
        self.report = Path(self.directory.name) / 'report.json'
        self.summary = Path(self.directory.name) / 'summary.md'
        self.write_csv(['https://old', 'https://new', 'https://new', ''])
        patch.object(urls.time, 'sleep').start()
        patch('sys.stdout', new_callable=io.StringIO).start()
        self.addCleanup(patch.stopall)

    def write_csv(self, values):
        with self.csv.open('w', newline='') as output:
            writer = csv.writer(output)
            writer.writerow(['Name', 'Batch', 'url'])
            writer.writerows([f'Product {i}', 'standard', value]
                             for i, value in enumerate(values))

    def validate(self, **kwargs):
        return urls.validate_csv_urls(str(self.csv), report=str(self.report),
                                      summary=str(self.summary), **kwargs)

    def test_full_scan_caches_and_reports_unique_counts(self):
        with patch.object(urls, 'validate_url', return_value=(True, '', False)) as check:
            self.assertTrue(self.validate())
        self.assertEqual(check.call_count, 2)
        result = json.loads(self.report.read_text())
        self.assertEqual(result['counts']['valid'], 2)
        self.assertEqual(result['counts']['checked_entries'], 3)
        self.assertEqual(result['counts']['cache_hits'], 1)
        self.assertEqual(len(result['checks']), 2)
        self.assertEqual(len(result['checks'][1]['entries']), 2)
        self.assertIn('valid: **2**', self.summary.read_text())

    def test_base_ref_only_new_values_and_git_uses_arguments(self):
        base = subprocess.CompletedProcess([], 0, 'Name,Batch,url\nOld,standard,https://old\n')
        with patch.object(urls.subprocess, 'run', return_value=base) as git:
            with patch.object(urls, 'validate_url', return_value=(True, '', False)) as check:
                self.assertTrue(self.validate(base_ref='main'))
        check.assert_called_once_with('https://new')
        command = git.call_args.args[0]
        self.assertEqual(command[:3], ['git', 'show', '--end-of-options'])
        self.assertEqual(command[3], f'main:{self.csv.relative_to(ROOT).as_posix()}')
        self.assertNotIn('shell', git.call_args.kwargs)
        result = json.loads(self.report.read_text())
        self.assertEqual(result['counts']['skipped_entries'], 1)
        self.assertEqual(result['counts']['checked_entries'], 2)

    def test_empty_diff_emits_report_without_network(self):
        with patch.object(urls, 'base_urls', return_value={'https://old', 'https://new'}):
            with patch.object(urls, 'validate_url') as check:
                self.assertTrue(self.validate(base_ref='main'))
        check.assert_not_called()
        result = json.loads(self.report.read_text())
        self.assertEqual(result['checks'], [])
        self.assertEqual(result['counts']['unique_urls'], 0)
        self.assertEqual(result['status'], 'ok')
        self.assertTrue(self.summary.exists())

    def test_invalid_base_is_error_not_empty_success(self):
        error = subprocess.CalledProcessError(128, ['git', 'show'], stderr='bad revision')
        with patch.object(urls.subprocess, 'run', side_effect=error):
            with patch.object(urls, 'validate_url') as check:
                self.assertFalse(self.validate(base_ref='missing'))
        check.assert_not_called()
        result = json.loads(self.report.read_text())
        self.assertEqual(result['status'], 'error')
        self.assertIn('bad revision', result['errors'][0])

    def test_empty_base_ref_fails_before_git_or_network(self):
        with patch.object(urls.subprocess, 'run') as git:
            with patch.object(urls, 'validate_url') as check:
                self.assertFalse(self.validate(base_ref=''))
        git.assert_not_called()
        check.assert_not_called()

    def test_malformed_base_csv_fails(self):
        base = subprocess.CompletedProcess([], 0, 'not,a,csv\n')
        with patch.object(urls.subprocess, 'run', return_value=base):
            self.assertFalse(self.validate(base_ref='main'))
        self.assertEqual(json.loads(self.report.read_text())['status'], 'error')

    def test_apply_clears_only_definitive_invalid(self):
        self.write_csv(['https://good', 'https://unknown', 'https://bad'])
        outcomes = [(True, '', False), (False, 'TLS unknown', True),
                    (False, 'HTTP 404', False)]
        with patch.object(urls, 'validate_url', side_effect=outcomes):
            self.assertTrue(self.validate(apply=True))
        with self.csv.open() as source:
            self.assertEqual([row['url'] for row in csv.DictReader(source)],
                             ['https://good', 'https://unknown', ''])
        result = json.loads(self.report.read_text())
        self.assertEqual([result['counts'][key] for key in ('valid', 'transient', 'invalid')],
                         [1, 1, 1])
        self.assertEqual(result['counts']['cleared_entries'], 1)

    def test_invalid_without_apply_fails_without_modifying_csv(self):
        original = self.csv.read_bytes()
        with patch.object(urls, 'validate_url', return_value=(False, 'HTTP 404', False)):
            self.assertFalse(self.validate())
        self.assertEqual(self.csv.read_bytes(), original)

    def test_empty_csv_with_header_reports_zero_checks(self):
        self.write_csv([])
        with patch.object(urls, 'validate_url') as check:
            self.assertTrue(self.validate())
        check.assert_not_called()
        self.assertEqual(json.loads(self.report.read_text())['checks'], [])

    def test_cli_empty_scan_writes_artifacts_and_appends_summary(self):
        self.write_csv([])
        self.summary.write_text('Existing summary\n')
        completed = subprocess.run(
            [sys.executable, str(ROOT / '.github/scripts/validate_urls.py'), str(self.csv),
             '--report', str(self.report), '--summary', str(self.summary)],
            capture_output=True, text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(self.report.read_text())['checks'], [])
        self.assertTrue(self.summary.read_text().startswith('Existing summary\n'))

    def test_cli_invalid_base_exits_nonzero_and_reports_error(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / '.github/scripts/validate_urls.py'), str(self.csv),
             '--base-ref', 'refs/heads/nonexistent-url-validator-test-ref',
             '--report', str(self.report)],
            capture_output=True, text=True,
        )
        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertEqual(json.loads(self.report.read_text())['status'], 'error')


if __name__ == '__main__':
    unittest.main()
