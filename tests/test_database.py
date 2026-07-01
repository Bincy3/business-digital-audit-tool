import os
import shutil
import tempfile
import unittest
from pathlib import Path

import database


class AuditDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="audittool-test-", dir=".")
        self.db_path = Path(self.temp_dir) / "audit_history.db"
        self.reports_dir = Path(self.temp_dir) / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        database.DB_PATH = self.db_path
        database.REPORTS_DIR = self.reports_dir
        database.init_db()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_add_and_read_audit_with_full_metadata(self):
        audit_id = database.add_audit(
            business_name="Acme Studio",
            industry="Marketing",
            website_url="https://acmestudio.com",
            overall_score=92,
            seo_score=90,
            technical_basics_score=88,
            social_presence_score=95,
            contact_readiness_score=94,
            conversion_readiness_score=91,
            html_filename="acme_20260101_120000.html",
            txt_filename="acme_20260101_120000.txt",
            recommendations=["Improve CTAs", "Fix alt text"],
            whatsapp_message="Hello from Acme",
            status="Complete",
        )

        saved_audit = database.get_audit(audit_id)
        self.assertIsNotNone(saved_audit)
        self.assertEqual(saved_audit["business_name"], "Acme Studio")
        self.assertEqual(saved_audit["industry"], "Marketing")
        self.assertEqual(saved_audit["seo_score"], 90)
        self.assertEqual(saved_audit["status"], "Complete")
        self.assertEqual(saved_audit["recommendations"], ["Improve CTAs", "Fix alt text"])


if __name__ == "__main__":
    unittest.main()
