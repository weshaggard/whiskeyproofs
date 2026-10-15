"""Focused, offline regression tests for the CSV and TTB validators."""

import contextlib
import csv
import http.client
import importlib.util
import io
from pathlib import Path
import socket
import ssl
import unittest
from unittest.mock import MagicMock, call, patch
import urllib.error
import uuid


ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(
        name, ROOT / '.github' / 'scripts' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


data = load_script('validate_whiskey_data')
ttb = load_script('validate_ttb_urls')


class CSVFixture(unittest.TestCase):
    def setUp(self):
        self.path = ROOT / 'tests' / f'.validator-{uuid.uuid4().hex}.csv'
        self.addCleanup(self.path.unlink, missing_ok=True)

    def row(self, **changes):
        row = dict(zip(data.CSV_FIELDS, (
            'Example', 'standard', '', '100', '1999-2026',
            'Example Distillery', 'Bourbon', '', '')))
        row.update(changes)
        return row

    def write_rows(self, rows):
        with self.path.open('w', encoding='utf-8', newline='') as output:
            writer = csv.DictWriter(output, fieldnames=data.CSV_FIELDS)
            writer.writeheader()
            writer.writerows(rows)

    def validate(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = data.validate_csv(self.path)
        return result, output.getvalue()


class CSVValidationTests(CSVFixture):
    def test_valid_optional_age_and_numeric_values(self):
        for age in ('', '7', '7.5', '6.25', '0'):
            for proof in ('90', '94.4', '110-125', '107.8-109.4'):
                with self.subTest(age=age, proof=proof):
                    self.write_rows([self.row(Age=age, Proof=proof)])
                    self.assertTrue(self.validate()[0])

    def test_proof_syntax_integer_formatting_and_order(self):
        for proof in ('.', '-', '1..2', '1-2-3', '90.', '.5', 'NaN',
                      'inf', '1e2', '-90', '0', '90.0', '90.00',
                      '110.0-125', '110-125.0', '125-110', '90 - 100'):
            with self.subTest(proof=proof):
                self.write_rows([self.row(Proof=proof)])
                valid, output = self.validate()
                self.assertFalse(valid)
                self.assertIn('Invalid proof', output)

    def test_age_rejects_ranges_and_excess_precision(self):
        for age in ('7-8', '-1', '6.125', 'NaN', '7.', '.5', '1e1'):
            with self.subTest(age=age):
                self.write_rows([self.row(Age=age)])
                valid, output = self.validate()
                self.assertFalse(valid)
                self.assertIn('Invalid Age', output)

    def test_invalid_release_years_fail_without_sort_crash(self):
        for year in ('', 'unknown', '2026-', '2026-2025', '1899-2026',
                     '1999', '2031', '2000-2031', '202A'):
            with self.subTest(year=year):
                self.write_rows([self.row(Batch='Fall', ReleaseYear=year),
                                 self.row(Batch='standard', ReleaseYear=year)])
                valid, output = self.validate()
                self.assertFalse(valid)
                self.assertIn('Invalid release year', output)

    def test_required_fields(self):
        for field in data.REQUIRED_FIELDS:
            with self.subTest(field=field):
                self.write_rows([self.row(**{field: ''})])
                valid, output = self.validate()
                self.assertFalse(valid)
                self.assertIn(f'Missing {field}', output)

    def test_empty_and_header_only_files(self):
        for contents in ('', ','.join(data.CSV_FIELDS) + '\n'):
            with self.subTest(contents=contents):
                self.path.write_text(contents, encoding='utf-8')
                self.assertFalse(self.validate()[0])

    def test_header_schema_diagnostics(self):
        cases = [
            (list(data.CSV_FIELDS[:-1]), 'missing columns'),
            (list(data.CSV_FIELDS) + ['Name'], 'duplicate column'),
            (list(data.CSV_FIELDS) + ['Extra'], 'unexpected columns'),
            (['name'] + list(data.CSV_FIELDS[1:]), 'missing columns'),
        ]
        for fields, diagnostic in cases:
            with self.subTest(fields=fields):
                self.path.write_text(','.join(fields) + '\n', encoding='utf-8')
                valid, output = self.validate()
                self.assertFalse(valid)
                self.assertIn(diagnostic, output)

    def test_malformed_rows_report_line_numbers(self):
        for line in ('Example,standard\n', ','.join(['x'] * 10) + '\n', '\n'):
            with self.subTest(line=line):
                self.path.write_text(','.join(data.CSV_FIELDS) + '\n' + line,
                                     encoding='utf-8')
                valid, output = self.validate()
                self.assertFalse(valid)
                self.assertIn('Line 2: Malformed row', output)

    def test_malformed_quoting_is_diagnostic(self):
        self.path.write_text(','.join(data.CSV_FIELDS) + '\n"unterminated',
                             encoding='utf-8')
        valid, output = self.validate()
        self.assertFalse(valid)
        self.assertIn('Error reading CSV file at line 2', output)

    def test_missing_file_is_diagnostic(self):
        valid, output = self.validate()
        self.assertFalse(valid)
        self.assertIn('Error reading CSV file', output)

    def test_utf8_bom_and_quoted_product_name(self):
        self.write_rows([self.row(Name='Example, "Special"')])
        self.path.write_text('\ufeff' + self.path.read_text(encoding='utf-8'),
                             encoding='utf-8')
        self.assertTrue(self.validate()[0])

    def test_duplicate_identity(self):
        self.write_rows([self.row(), self.row()])
        valid, output = self.validate()
        self.assertFalse(valid)
        self.assertIn('Line 3: Duplicate', output)

    def test_product_order_and_contiguity(self):
        self.write_rows([self.row(Name='A', Batch='2026'),
                         self.row(Name='B'), self.row(Name='A', Batch='2025')])
        valid, output = self.validate()
        self.assertFalse(valid)
        self.assertIn('not contiguous', output)
        self.assertIn('not in alphabetical order', output)

    def test_batch_sort_failure(self):
        self.write_rows([self.row(Batch='Batch 2'), self.row(Batch='Batch 15')])
        valid, output = self.validate()
        self.assertFalse(valid)
        self.assertIn("batch 'Batch 15' should come before 'Batch 2'", output)


class BatchSortTests(unittest.TestCase):
    def test_documented_batch_patterns(self):
        cases = [
            [('2026-04', '2026'), ('2026-03', '2026'), ('2025-04', '2025')],
            [('Fall 2026', '2026'), ('Spring 2026', '2026'), ('Fall 2025', '2025')],
            [('A126', '2026'), ('C925', '2025'), ('B525', '2025'), ('A125', '2025')],
            [('Batch 15', '2026'), ('Batch 14', '2026'), ('Batch 3', '2025'),
             ('Batch 2', '2025'), ('Batch 1', '2024')],
            [('18', '2025'), ('17', '2025'), ('2', '2024')],
            [('Chapter 10', '2026'), ('Chapter 9', '2025'), ('Chapter 2', '2024')],
            [('25C', '2025'), ('25A', '2025'), ('24D', '2024')],
            [('6 - LA/NE (Spring 2025)', '2025'), ('5 - LL/LE (Fall 2024)', '2024')],
            [('2026', '2026'), ('2025', '2025'), ('2016', '2016')],
            [('2017 (Other States)', '2017'), ('2017 (FL/GA/KY)', '2017')],
            [('Pact 11', '2026'), ('Pact 10', '2025'), ('Pact 2', '2017')],
            [('Series IX', '2026'), ('Series VIII', '2025'), ('Series II', '2020')],
            [('Series 15', '2026'), ('Series 9', '2025')],
            [('Toasted Barrel Sour Mash', '2025'), ('Toasted Barrel Sour Mash', '2022'),
             ('Toasted Barrel Rye', '2023'), ('Toasted Barrel Bourbon', '2024'),
             ('Barrel Strength Rye', '2025'), ('Barrel Strength Bourbon', '2017-2025')],
        ]
        for batches in cases:
            with self.subTest(batches=batches):
                self.assertEqual(batches, sorted(
                    reversed(batches), key=lambda item: data.batch_sort_key(*item)))

    def test_uniform_keys_for_mixed_year_season_parenthetical_batches(self):
        batches = [('2025', '2025'), ('Fall 2025', '2025'),
                   ('Spring 2025', '2025'), ('2025 (Other States)', '2025'),
                   ('2025 (FL/GA/KY)', '2025'), ('2024', '2024')]
        keys = [data.batch_sort_key(*batch) for batch in batches]
        self.assertEqual(1, len({tuple(type(part) for part in key) for key in keys}))
        result = sorted(batches, key=lambda item: data.batch_sort_key(*item))
        self.assertEqual([
            ('2025 (Other States)', '2025'),
            ('2025 (FL/GA/KY)', '2025'), ('2025', '2025'),
            ('Fall 2025', '2025'),
            ('Spring 2025', '2025'), ('2024', '2024')], result)

    def test_all_patterns_comparable_and_invalid_year_does_not_crash(self):
        batches = ['2025-04', '6 - LA/NE (Spring 2025)', 'Fall 2025', 'C925',
                   'Batch 15', '2025', '18', 'Chapter 9', 'Pact 11', 'Series IX',
                   '25C', '2017 (Other States)', 'standard']
        keys = [data.batch_sort_key(batch, year)
                for batch in batches for year in ('2025', '1999-2025', '', 'bad')]
        self.assertEqual(1, len({tuple(type(part) for part in key) for key in keys}))
        self.assertEqual(len(keys), len(sorted(keys)))


class TTBValidationTests(CSVFixture):
    ttb_id = '25001001000001'

    def response(self, status=200, body=b'TTB ID: 25001001000001'):
        response = MagicMock()
        response.status = status
        response.read.return_value = body
        response.__enter__.return_value = response
        return response

    def http_error(self, status):
        return urllib.error.HTTPError('https://ttbonline.gov/', status, 'error', {}, None)

    def test_url_generation_both_formats(self):
        self.assertIn('publicViewImage.do?id=08001001000001',
                      ttb.generate_ttb_url('08001001000001'))
        for prefix in ('09', '25', '99'):
            with self.subTest(prefix=prefix):
                self.assertIn('viewColaDetails.do', ttb.generate_ttb_url(prefix + '001001000001'))

    def test_valid_response_uses_get_timeout_closes_and_preserves_tls(self):
        response = self.response()
        with patch.object(ttb.urllib.request, 'urlopen', return_value=response) as request:
            valid, _, error = ttb.validate_ttb_url(self.ttb_id, timeout=7)
        self.assertIs(valid, True)
        self.assertEqual('', error)
        self.assertEqual({'timeout': 7}, request.call_args.kwargs)
        self.assertEqual('GET', request.call_args.args[0].method)
        response.read.assert_called_once_with(ttb.MAX_CONTENT_BYTES)
        response.__exit__.assert_called_once()

    def test_explicit_error_and_definitive_http_failures(self):
        cases = [self.response(body=b'Unable to process request'),
                 self.response(body=b'unable to PROCESS request'),
                 self.http_error(404), self.http_error(410),
                 self.response(status=404), self.response(status=410)]
        for result in cases:
            with self.subTest(result=result):
                with patch.object(ttb.urllib.request, 'urlopen') as request, \
                        patch.object(ttb.time, 'sleep') as sleep:
                    if isinstance(result, Exception):
                        request.side_effect = result
                    else:
                        request.return_value = result
                    self.assertIs(ttb.validate_ttb_url(self.ttb_id)[0], False)
                    request.assert_called_once()
                    sleep.assert_not_called()

    def test_transient_errors_have_at_most_three_bounded_retries(self):
        errors = [
            self.http_error(429), self.http_error(500), self.http_error(503),
            self.http_error(408), self.response(status=502),
            urllib.error.URLError(socket.gaierror('DNS failure')),
            urllib.error.URLError('connection refused'), TimeoutError('timed out'),
            http.client.RemoteDisconnected('closed'),
            http.client.IncompleteRead(b'partial'),
        ]
        for error in errors:
            with self.subTest(error=error):
                with patch.object(ttb.urllib.request, 'urlopen') as request, \
                        patch.object(ttb.time, 'sleep') as sleep:
                    if isinstance(error, Exception):
                        request.side_effect = error
                    else:
                        request.return_value = error
                    valid, _, reason = ttb.validate_ttb_url(self.ttb_id)
                    self.assertIsNone(valid)
                    self.assertTrue(reason)
                    self.assertEqual(4, request.call_count)
                    self.assertEqual([call(1), call(2), call(4)], sleep.call_args_list)

    def test_retry_can_recover_or_confirm_invalid(self):
        for response, expected in ((self.response(), True),
                                   (self.response(body=b'Unable to process request'), False)):
            with self.subTest(expected=expected):
                with patch.object(ttb.urllib.request, 'urlopen',
                                  side_effect=[self.http_error(503), response]) as request, \
                        patch.object(ttb.time, 'sleep') as sleep:
                    self.assertIs(ttb.validate_ttb_url(self.ttb_id)[0], expected)
                    self.assertEqual(2, request.call_count)
                    sleep.assert_called_once_with(1)

    def test_tls_unknown_and_unknown_errors_do_not_retry_or_disable_verification(self):
        errors = [ssl.SSLCertVerificationError('certificate verify failed'),
                  urllib.error.URLError(ssl.SSLError('TLS failure')),
                  self.http_error(403), self.http_error(401), self.http_error(302),
                  ValueError('unexpected failure')]
        for error in errors:
            with self.subTest(error=error):
                with patch.object(ttb.urllib.request, 'urlopen', side_effect=error) as request, \
                        patch.object(ttb.time, 'sleep') as sleep:
                    self.assertIsNone(ttb.validate_ttb_url(self.ttb_id)[0])
                    request.assert_called_once()
                    self.assertNotIn('context', request.call_args.kwargs)
                    sleep.assert_not_called()

    def test_empty_or_unrecognized_success_is_unknown(self):
        for body in (b'', b'<html>Sign in</html>', b'Service unavailable'):
            with self.subTest(body=body):
                with patch.object(ttb.urllib.request, 'urlopen',
                                  return_value=self.response(body=body)):
                    self.assertIsNone(ttb.validate_ttb_url(self.ttb_id)[0])

    def test_apply_only_clears_confirmed_invalid_and_caches_results(self):
        self.write_rows([
            self.row(Name='A', TTB_ID='bad'),
            self.row(Name='B', TTB_ID='bad'),
            self.row(Name='C', TTB_ID='unknown'),
            self.row(Name='D', TTB_ID='good')])
        before = list(csv.DictReader(io.StringIO(self.path.read_text())))
        results = [(False, 'url', 'HTTP 404'), (None, 'url', 'HTTP 429'),
                   (True, 'url', '')]
        output = io.StringIO()
        with patch.object(ttb, 'validate_ttb_url', side_effect=results) as validate, \
                patch.object(ttb.time, 'sleep'), contextlib.redirect_stdout(output):
            self.assertTrue(ttb.validate_and_update_csv(self.path, delay=0, dry_run=False))
        after = list(csv.DictReader(io.StringIO(self.path.read_text())))
        self.assertEqual(3, validate.call_count)
        self.assertEqual(['', '', 'unknown', 'good'], [row['TTB_ID'] for row in after])
        for old, new in zip(before, after):
            old.pop('TTB_ID')
            new.pop('TTB_ID')
            self.assertEqual(old, new)
        self.assertIn('unverified', output.getvalue())
        self.assertNotIn('All TTB IDs are verified valid', output.getvalue())

    def test_unknown_only_apply_does_not_write_or_claim_all_valid(self):
        self.write_rows([self.row(TTB_ID=self.ttb_id)])
        original = self.path.read_bytes()
        output = io.StringIO()
        with patch.object(ttb, 'validate_ttb_url', return_value=(None, 'url', 'TLS error')), \
                patch.object(ttb.time, 'sleep'), contextlib.redirect_stdout(output):
            self.assertTrue(ttb.validate_and_update_csv(self.path, dry_run=False))
        self.assertEqual(original, self.path.read_bytes())
        self.assertIn('some IDs remain unverified', output.getvalue())
        self.assertNotIn('All TTB IDs are verified valid', output.getvalue())

    def test_cli_dry_run_fails_and_apply_succeeds(self):
        for apply in (False, True):
            with self.subTest(apply=apply):
                self.write_rows([self.row(TTB_ID=self.ttb_id)])
                original = self.path.read_bytes()
                argv = ['validate_ttb_urls.py', '--csv', str(self.path), '--delay', '0']
                if apply:
                    argv.append('--apply')
                with patch.object(ttb.sys, 'argv', argv), \
                        patch.object(ttb.urllib.request, 'urlopen',
                                     return_value=self.response(body=b'Unable to process request')), \
                        patch.object(ttb.time, 'sleep'), contextlib.redirect_stdout(io.StringIO()), \
                        self.assertRaises(SystemExit) as exit_status:
                    ttb.main()
                self.assertEqual(0 if apply else 1, exit_status.exception.code)
                if not apply:
                    self.assertEqual(original, self.path.read_bytes())
                else:
                    rows = list(csv.DictReader(io.StringIO(self.path.read_text())))
                    self.assertEqual('', rows[0]['TTB_ID'])

    def test_apply_retains_ids_for_all_unverified_http_and_network_failures(self):
        errors = [self.http_error(429), self.http_error(503), self.http_error(403),
                  urllib.error.URLError(socket.gaierror('DNS failure')),
                  ssl.SSLCertVerificationError('TLS failure'),
                  TimeoutError('timed out'), RuntimeError('unknown')]
        for error in errors:
            with self.subTest(error=error):
                self.write_rows([self.row(TTB_ID=self.ttb_id)])
                original = self.path.read_bytes()
                with patch.object(ttb.urllib.request, 'urlopen', side_effect=error), \
                        patch.object(ttb.time, 'sleep'), contextlib.redirect_stdout(io.StringIO()):
                    self.assertTrue(ttb.validate_and_update_csv(self.path, dry_run=False))
                self.assertEqual(original, self.path.read_bytes())


if __name__ == '__main__':
    unittest.main()
