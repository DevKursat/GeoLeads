"""
Unit tests for SQLite Database operations.
"""
import unittest
import os
import tempfile
from app.core.database import Database
from app.models import Lead, CRMStage, SalesGap, OpportunitySeverity


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.db = Database(db_path=self.temp_db.name)

    def tearDown(self):
        try:
            os.remove(self.temp_db.name)
        except Exception:
            pass

    def test_save_and_retrieve_lead(self):
        lead = Lead(
            place_id="test_place_1",
            name="Test Diş Hekimi",
            category="Sağlık",
            city="Kadıköy",
            phone="+90 532 100 20 30",
            website="https://testdis.com",
            has_website=True,
            opportunity_score=65,
            emails=["info@testdis.com"],
            gaps=[SalesGap(
                code="FEW_REVIEWS",
                title="Az Yorum",
                description="Yorum az",
                severity=OpportunitySeverity.MEDIUM,
                pitch_angle="Yorum artırma",
                suggested_solution="NFC Yorum"
            )]
        )
        saved = self.db.save_or_update_lead(lead)
        self.assertIsNotNone(saved.id)

        retrieved = self.db.get_lead(saved.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Test Diş Hekimi")
        self.assertEqual(retrieved.emails, ["info@testdis.com"])
        self.assertEqual(len(retrieved.gaps), 1)
        self.assertEqual(retrieved.gaps[0].code, "FEW_REVIEWS")

    def test_update_crm_stage(self):
        lead = Lead(name="CRM Deneme", city="İstanbul")
        saved = self.db.save_or_update_lead(lead)

        self.db.update_crm_stage(saved.id, CRMStage.CONTACTED, notes="Görüşme sağlandı")
        updated = self.db.get_lead(saved.id)
        self.assertEqual(updated.crm_stage, CRMStage.CONTACTED)
        self.assertEqual(updated.notes, "Görüşme sağlandı")

    def test_stats_aggregation(self):
        lead1 = Lead(name="L1", city="İst", phone="+90555", has_website=False, opportunity_score=80)
        lead2 = Lead(name="L2", city="İst", emails=["a@b.com"], has_website=True, opportunity_score=40)
        self.db.save_or_update_lead(lead1)
        self.db.save_or_update_lead(lead2)

        stats = self.db.get_stats()
        self.assertEqual(stats["total_leads"], 2)
        self.assertEqual(stats["with_phone"], 1)
        self.assertEqual(stats["with_email"], 1)
        self.assertEqual(stats["missing_website"], 1)
        self.assertEqual(stats["high_opportunity"], 1)


if __name__ == "__main__":
    unittest.main()
