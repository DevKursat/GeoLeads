"""
Unit tests for GapDetector and Opportunity Scoring.
"""
import unittest
from app.models import Lead, CRMStage
from app.services.gap_detector import GapDetector


class TestGapDetector(unittest.TestCase):
    def test_missing_website_detected(self):
        lead = Lead(
            name="Test Kebapçısı",
            city="İstanbul",
            website="",
            has_website=False,
            phone="+90 532 111 22 33"
        )
        score, gaps, primary_gap = GapDetector.analyze(lead)
        self.assertGreaterEqual(score, 50)
        gap_codes = [g.code for g in gaps]
        self.assertIn("MISSING_WEBSITE", gap_codes)
        self.assertEqual(primary_gap, "MISSING_WEBSITE")

    def test_insecure_ssl_detected(self):
        lead = Lead(
            name="Hukuk Bürosu",
            city="Ankara",
            website="http://www.avukatankara.com",
            has_website=True,
            has_ssl=False
        )
        score, gaps, primary_gap = GapDetector.analyze(lead)
        gap_codes = [g.code for g in gaps]
        self.assertIn("NO_SSL_INSECURE", gap_codes)

    def test_low_rating_detected(self):
        lead = Lead(
            name="Oto Servis",
            city="İzmir",
            website="https://www.otoservis.com",
            has_website=True,
            has_ssl=True,
            rating=3.7,
            review_count=25
        )
        score, gaps, primary_gap = GapDetector.analyze(lead)
        gap_codes = [g.code for g in gaps]
        self.assertIn("LOW_RATING", gap_codes)


if __name__ == "__main__":
    unittest.main()
