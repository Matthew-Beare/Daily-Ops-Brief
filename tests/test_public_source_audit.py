from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audit_public_source", ROOT / "scripts/audit_public_source.py")
AUDIT = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(AUDIT)


class PublicSourceAuditTests(unittest.TestCase):
    def test_clean_source_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            (root / "README.md").write_text("No credentials here.\n", encoding="utf-8")
            self.assertEqual([], AUDIT.audit(root))

    def test_private_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            (root / "bad.txt").write_text(
                "-----BEGIN PRIVATE KEY-----\nnot-real-but-forbidden\n",
                encoding="utf-8",
            )
            errors = AUDIT.audit(root)
            self.assertTrue(any("private key" in error for error in errors))

    def test_token_like_secret_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            (root / "bad.txt").write_text(
                "token = 'ghp_abcdefghijklmnopqrstuvwxyzABCDEF1234567890'\n",
                encoding="utf-8",
            )
            errors = AUDIT.audit(root)
            self.assertTrue(any("GitHub token" in error or "literal secret" in error for error in errors))

    def test_placeholder_assignment_is_allowed(self) -> None:
        errors = AUDIT.scan_text('client_secret = "YOUR_CLIENT_SECRET_PLACEHOLDER"', "fixture")
        self.assertEqual([], errors)

    def test_blocked_mutable_export_type_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            (root / "live.sqlite").write_bytes(b"sqlite")
            errors = AUDIT.audit(root)
            self.assertTrue(any("mutable-data file type" in error for error in errors))

    def test_valid_luhn_card_number_is_rejected(self) -> None:
        errors = AUDIT.scan_text("card 4111 1111 1111 1111", "fixture")
        self.assertTrue(any("payment-card" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
