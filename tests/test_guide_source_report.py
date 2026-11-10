"""The delivery renderer must refresh evidence before declaring completion."""

from pathlib import Path
import contextlib
import csv
import hashlib
import importlib.util
import io
import json
import subprocess
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATION = load_module('guide_code_validation')
REPORT = load_module('guide_source_report')


class SourceReportFreshnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.art = self.root / 'artifacts'
        self.art.mkdir()
        for locale in ('zh', 'en'):
            self.write(f'docs/{locale}/guides/task.md',
                       '---\ntitle: Task\n---\n\n# Task\n\nReviewed steps.\n')
        self.write('artifacts/source.cpp', 'entry\ncommand\nresult\n')
        self.row = {'Feature ID': 'IMG-001',
                    'Documentation path and section': 'docs/zh/guides/task.md#task'}
        item = {'feature_id': 'IMG-001', 'code_result': 'source_pass', 'gaps': [],
                'chain': dict.fromkeys(('entry', 'event', 'processing', 'result',
                                       'options_and_limits'), 'reviewed'),
                'source_refs': ['artifacts/source.cpp#L1-3']}
        for locale in ('zh', 'en'):
            path = f'docs/{locale}/guides/task.md'
            item[locale + '_path'] = path
            item[locale + '_sha256'] = VALIDATION.digest(self.root / path)
        sources = {'artifacts/source.cpp': VALIDATION.digest(self.art / 'source.cpp')}
        audit = self.write_json('audit.json', {'items': [item]})
        audit['peer_review'] = self.write_json(
            'peer.json', {'proposal_sha256': audit['sha256'], 'result': 'pass',
                          'gaps': [], 'feature_ids': ['IMG-001']})
        asset = self.write_json('asset.json', {'items': [
            {'feature_id': 'IMG-001', 'result': 'complete',
             'rationale': 'The reviewed task illustration.', 'asset_hashes': sources}]})
        website = self.write_json('website.json', {
            'result': 'pass', 'gaps': [], 'checks': {'fixture': 'pass'},
            'current_inputs': {'pages': {
                item[locale + '_path']: item[locale + '_sha256']
                for locale in ('zh', 'en')}}})
        source = self.write_json('source-verification.json', {
            'result': 'pass', 'errors': [], 'source_hashes': sources})
        self.write_json('guide-code-validation-inputs.json', {
            'source_commit': 'f02f50e5c6b132335247079398944b6fc9f7e6d6',
            'audits': [audit], 'source_hashes': sources,
            'source_verification': source, 'asset_review': asset, 'website_review': website})
        self.write_json('guide-validation-policy.json', {
            'mode': 'source_analysis', 'instruction': 'Verify from code.'})
        self.write_json('guide-site-check.json', {})
        self.write_json('guide-acceptance-evaluation.json', {'strict_complete': 0, 'items': []})
        self.write('artifacts/guide-acceptance-evidence.csv', 'Result,Kind\npending,native\n')
        self.write('artifacts/guide-acceptance-scopes.csv', 'Scope ID\nlegacy\n')
        self.native_before = self.native_bytes()
        self.write_json('fixture-rows.json', [self.row])
        self.write_coverage([self.row])
        # This test adapter isolates legacy anchor/build requirements, while calling the
        # same real evidence validator as the production checker in a separate process.
        self.checker = self.write('scripts/check-guide-coverage.py', f'''
from pathlib import Path
import csv, importlib.util, json
spec = importlib.util.spec_from_file_location('validation', {str(SCRIPTS / 'guide_code_validation.py')!r})
validation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validation)
root = Path(__file__).resolve().parents[1]
rows = json.loads((root / 'artifacts/fixture-rows.json').read_text())
validation.evaluate_all(root, rows, [], {{}})
with (root / 'artifacts/guide-coverage.csv').open('w', newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
''')
        initial = VALIDATION.evaluate_all(self.root, [dict(self.row)], [], {})
        self.assertEqual(initial['complete_operations'], 1)

    def write(self, path, contents):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(contents)
        return target

    def write_json(self, name, data):
        path = self.write('artifacts/' + name, json.dumps(data))
        return {'path': 'artifacts/' + name,
                'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

    def write_coverage(self, rows):
        with (self.art / 'guide-coverage.csv').open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def native_bytes(self):
        return [(self.art / name).read_bytes() for name in
                ('guide-acceptance-evidence.csv', 'guide-acceptance-scopes.csv')]

    def render(self):
        with contextlib.redirect_stdout(io.StringIO()):
            REPORT.render(self.root)
        return json.loads((self.art / 'guide-delivery.json').read_text())

    def test_current_evidence_still_completes_without_touching_native_history(self):
        report = self.render()
        self.assertEqual(report['status'], 'complete_by_user_requested_source_analysis')
        self.assertEqual(report['completed_operations'], 1)
        self.assertEqual(self.native_bytes(), self.native_before)

    def test_changed_translation_refreshes_cached_green_evaluation(self):
        self.write('docs/en/guides/task.md',
                   '---\ntitle: Task\n---\n\n# Task\n\nUnreviewed new steps.\n')
        report = self.render()
        self.assertEqual(report['status'], 'partial_source_analysis')
        self.assertEqual(report['completed_operations'], 0)
        self.assertEqual(report['incomplete_operations'], 1)
        self.assertIn('IMG-001', (self.art / 'guide-pending.csv').read_text())
        self.assertEqual(self.native_bytes(), self.native_before)

    def test_changed_review_binding_cannot_reuse_cached_green_evaluation(self):
        self.write_json('peer.json', {})
        report = self.render()
        self.assertEqual(report['status'], 'partial_source_analysis')
        self.assertEqual(report['completed_operations'], 0)
        self.assertEqual(self.native_bytes(), self.native_before)

    def test_checker_failure_cannot_publish_completed_report(self):
        self.checker.write_text('raise SystemExit(3)\n')
        with self.assertRaises(subprocess.CalledProcessError):
            self.render()
        self.assertFalse((self.art / 'guide-delivery.json').exists())
        self.assertEqual(self.native_bytes(), self.native_before)


if __name__ == '__main__':
    unittest.main()
