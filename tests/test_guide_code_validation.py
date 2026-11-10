"""Regression checks for evidence integrity when the user selects code validation."""

from pathlib import Path
import copy
import importlib.util
import json
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location(
    'guide_code_validation', Path(__file__).resolve().parents[1] / 'scripts/guide_code_validation.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SourceEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name, content in [('docs/zh/guides/a.md', '# Task'), ('docs/en/guides/a.md', '# Task'),
                              ('artifacts/source.cpp', 'entry\ncommand\nresult\n')]:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        self.row = {'Documentation path and section': 'docs/zh/guides/a.md#task'}
        self.item = {'code_result': 'source_pass', 'gaps': [],
                     'chain': dict.fromkeys(('entry', 'event', 'processing', 'result', 'options_and_limits'), 'reviewed'),
                     'source_refs': ['artifacts/source.cpp#L1-3']}
        for locale in ('zh', 'en'):
            path = f'docs/{locale}/guides/a.md'
            self.item[locale + '_path'] = path
            self.item[locale + '_sha256'] = MODULE.digest(self.root / path)
        self.sources = {'artifacts/source.cpp': MODULE.digest(self.root / 'artifacts/source.cpp')}

    def gaps(self, item=None, sources=None):
        return MODULE.item_gaps(self.root, self.row, item or self.item,
                                self.sources if sources is None else sources)

    def test_current_review_is_accepted(self):
        self.assertEqual(self.gaps(), [])

    def test_translation_edit_invalidates_review(self):
        (self.root / 'docs/en/guides/a.md').write_text('changed behavior')
        self.assertTrue(any('en' in gap for gap in self.gaps()))

    def test_scope_gate_alone_is_not_a_workflow(self):
        item = copy.deepcopy(self.item)
        del item['chain']['processing']
        self.assertTrue(any('processing' in gap for gap in self.gaps(item)))

    def test_source_edits_and_out_of_range_citations_are_rejected(self):
        (self.root / 'artifacts/source.cpp').write_text('different\n')
        self.assertTrue(self.gaps())
        self.sources['artifacts/source.cpp'] = MODULE.digest(self.root / 'artifacts/source.cpp')
        self.assertTrue(any('行号' in gap for gap in self.gaps()))

    def test_unbound_source_is_rejected(self):
        self.assertTrue(self.gaps(sources={}))

    def test_edition_platform_gates_are_bound_and_current(self):
        gate = self.root / 'artifacts/gate.cpp'
        gate.write_text('full\nmini\n')
        item = copy.deepcopy(self.item)
        item['gate_refs'] = ['artifacts/gate.cpp#L1-2']
        sources = {**self.sources, 'artifacts/gate.cpp': MODULE.digest(gate)}
        self.assertEqual(self.gaps(item, sources), [])

        with self.subTest('unbound gate'):
            self.assertTrue(self.gaps(item, self.sources))
        with self.subTest('changed gate'):
            gate.write_text('different edition condition\n')
            self.assertTrue(self.gaps(item, sources))
        with self.subTest('out-of-range gate'):
            sources['artifacts/gate.cpp'] = MODULE.digest(gate)
            self.assertTrue(self.gaps(item, sources))
        with self.subTest('missing gate'):
            gate.unlink()
            self.assertTrue(self.gaps(item, sources))

    def test_pending_gap_cannot_be_promoted_by_source_presence(self):
        item = copy.deepcopy(self.item)
        item['code_result'] = 'pending'
        item['gaps'] = ['wrong toolbar path']
        self.assertIn('wrong toolbar path', self.gaps(item))
        self.assertGreater(len(self.gaps(item)), 1)

    def test_policy_does_not_accept_missing_review_inputs(self):
        row = {'Feature ID': 'IMG-001', **self.row}
        result = MODULE.evaluate_all(self.root, [row], [], {})
        self.assertEqual(result['complete_operations'], 0)
        self.assertEqual(result['pending_operations'], 1)

    def test_signed_current_audit_accepts_without_rewriting_native_ledger(self):
        art = self.root / 'artifacts'
        native = art / 'guide-acceptance-evidence.csv'
        native.write_text('Result,Kind\npending,native\n')
        before = native.read_bytes()

        def write(name, data):
            path = art / name
            path.write_text(json.dumps(data))
            return {'path': 'artifacts/' + name, 'sha256': MODULE.digest(path)}

        item = {'feature_id': 'IMG-001', **self.item}
        audit = write('audit.json', {'items': [item]})
        peer = write('peer.json', {'proposal_sha256': audit['sha256'], 'result': 'pass',
                                   'gaps': [], 'feature_ids': ['IMG-001']})
        audit['peer_review'] = peer
        asset = write('asset.json', {'items': [{'feature_id': 'IMG-001', 'result': 'complete',
                                                'rationale': 'specific operation diagram',
                                                'asset_hashes': self.sources}]})
        website = write('website.json', {'result': 'pass', 'gaps': [],
                                         'current_inputs': {'pages': {'docs/en/guides/a.md': self.item['en_sha256']}}})
        source = write('source-verification.json', {'result': 'pass', 'errors': [], 'source_hashes': self.sources})
        write('guide-code-validation-inputs.json', {'source_commit': 'f02f50e5c6b132335247079398944b6fc9f7e6d6',
                                                   'audits': [audit], 'source_hashes': self.sources,
                                                   'source_verification': source,
                                                   'asset_review': asset, 'website_review': website})
        row = {'Feature ID': 'IMG-001', **self.row}
        result = MODULE.evaluate_all(self.root, [row], [], {})
        self.assertEqual(result['complete_operations'], 1)
        self.assertEqual(native.read_bytes(), before)
        # Changing the audit without a new independent signature must fail closed.
        (art / 'peer.json').write_text('{}')
        result = MODULE.evaluate_all(self.root, [row], [], {})
        self.assertEqual(result['complete_operations'], 0)


if __name__ == '__main__':
    unittest.main()
