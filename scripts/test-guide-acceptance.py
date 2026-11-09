import csv
import hashlib
from pathlib import Path
import tempfile
import unittest

from guide_acceptance import (
    CRITERIA, EVIDENCE_COLUMNS, REQUIRED_KIND, SCOPE_COLUMNS,
    evaluate, load_inputs, status_text,
)


class AcceptanceContract(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.doc = self.root / "docs/zh/guides/example.md"
        self.doc.parent.mkdir(parents=True)
        self.doc.write_text("# Test tutorial\n", encoding="utf-8")
        (self.root / "artifacts").mkdir()
        (self.root / "artifacts/proof.txt").write_text("Isolated unit fixture, not product evidence.")
        self.row = {
            "Feature ID": "TEST-001",
            "Product version and platform": "1.5.2 Windows/macOS Full",
            "Documentation path and section": "docs/zh/guides/example.md#test",
            "Availability conclusion": "release source chain reviewed",
        }

    def scope(self, sid="macos-arm64-full", platform="macOS"):
        return dict(zip(SCOPE_COLUMNS, [
            "TEST-001", sid, "1.5.2", platform, "Full", "arm64" if platform == "macOS" else "x64",
            hashlib.sha256(self.doc.read_bytes()).hexdigest(),
            "docs/zh/guides/example.md;artifacts/proof.txt", "reviewed", "test-fixture",
            "Unit fixture explicitly declares this advertised platform.",
        ]))

    def proofs(self, sid="macos-arm64-full"):
        return [
            dict(zip(EVIDENCE_COLUMNS, [
                "TEST-001", sid, "1.5.2", criterion, "pass", REQUIRED_KIND[criterion],
                "release" if criterion in {"availability", "workflow", "result", "options-limitations"} else "website",
                "artifacts/proof.txt", "reviewed", "test-fixture",
                "Unit fixture for reviewed criterion; not actual Snow Shot verification.",
            ]))
            for criterion in CRITERIA
        ]

    def write(self, filename, columns, rows):
        with (self.root / "artifacts" / filename).open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

    def test_source_and_build_cannot_automatically_complete(self):
        proof = self.proofs()
        for item in proof:
            item["Evidence kind"] = "source"
            item["Build channel"] = "source"
        result = evaluate(self.root, self.row, [self.scope()], proof)
        self.assertFalse(result["complete"])
        self.assertEqual(len(result["scopes"][0]["missing_criteria"]), 7)

    def test_platform_partial_is_preserved_and_full_scope_can_complete(self):
        scopes = [self.scope(), self.scope("windows-x64-full", "Windows")]
        proof = self.proofs()
        first = evaluate(self.root, self.row, scopes, proof)
        self.assertFalse(first["complete"])
        self.assertEqual(first["accepted_scopes"], ["macos-arm64-full"])
        proof += self.proofs("windows-x64-full")
        final = evaluate(self.root, self.row, scopes, proof)
        self.assertTrue(final["complete"])
        self.assertTrue(status_text(final).startswith("已完成"))
        self.assertEqual(final, evaluate(self.root, self.row, scopes, proof))

    def test_development_runtime_is_reference_not_release_acceptance(self):
        proof = self.proofs()
        proof[1]["Build channel"] = "development"
        proof[2]["Evidence kind"] = "backend_result"
        result = evaluate(self.root, self.row, [self.scope()], proof)
        self.assertFalse(result["complete"])
        self.assertIn("workflow", result["scopes"][0]["missing_criteria"])
        self.assertIn("result", result["scopes"][0]["missing_criteria"])
        self.assertEqual(len(result["scopes"][0]["reference_evidence"]), 7)

    def test_known_asset_or_site_gap_overrides_attestation(self):
        self.assertFalse(evaluate(self.root, self.row, [self.scope()], self.proofs(), asset_gap=True)["complete"])
        self.assertFalse(evaluate(self.root, self.row, [self.scope()], self.proofs(), website_ok=False)["complete"])

    def test_changed_content_requires_new_review(self):
        scope = self.scope()
        self.doc.write_text("# Changed tutorial\n")
        result = evaluate(self.root, self.row, [scope], self.proofs())
        self.assertFalse(result["complete"])
        self.assertEqual(len(result["scopes"][0]["missing_criteria"]), 7)

    def test_unreleased_candidate_cannot_be_promoted(self):
        self.row["Availability conclusion"] = "未发行：later commit"
        self.assertFalse(evaluate(self.root, self.row, [self.scope()], self.proofs())["complete"])

    def test_schema_rejects_waiving_workflow(self):
        proof = self.proofs()
        proof[1]["Result"] = "not_applicable"
        self.write("guide-acceptance-scopes.csv", SCOPE_COLUMNS, [self.scope()])
        self.write("guide-acceptance-evidence.csv", EVIDENCE_COLUMNS, proof)
        with self.assertRaisesRegex(ValueError, "cannot be waived"):
            load_inputs(self.root, [self.row])

    def test_reviewed_evidence_requires_real_reference(self):
        proof = self.proofs()
        proof[0]["Evidence refs"] = "artifacts/nonexistent.txt"
        self.write("guide-acceptance-scopes.csv", SCOPE_COLUMNS, [self.scope()])
        self.write("guide-acceptance-evidence.csv", EVIDENCE_COLUMNS, proof)
        with self.assertRaisesRegex(ValueError, "usable references"):
            load_inputs(self.root, [self.row])

    def test_reviewed_scopes_and_valid_proofs_load(self):
        self.write("guide-acceptance-scopes.csv", SCOPE_COLUMNS, [self.scope()])
        self.write("guide-acceptance-evidence.csv", EVIDENCE_COLUMNS, self.proofs())
        scopes, proofs = load_inputs(self.root, [self.row])
        self.assertTrue(evaluate(self.root, self.row, scopes, proofs)["complete"])


if __name__ == "__main__":
    unittest.main()
