"""
Unit tests for AI Pitch Generator.
"""
import unittest
from app.models import Lead
from app.services.pitch_generator import PitchGenerator


class TestPitchGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = PitchGenerator()
        self.lead = Lead(
            name="Kadıköy Estetik Diş",
            category="Diş Hekimi",
            city="Kadıköy",
            phone="+90 532 999 88 77",
            whatsapp="https://wa.me/905329998877",
            primary_gap="MISSING_WEBSITE",
            rating=4.8,
            review_count=35
        )

    def test_generate_turkish_whatsapp_pitch(self):
        res = self.generator.generate_pitch(
            lead=self.lead,
            channel="whatsapp",
            tone="consultative",
            lang="tr",
            custom_sender_name="Kürşat",
            custom_agency_name="Büyüme Ajansı"
        )
        self.assertEqual(res["channel"], "whatsapp")
        self.assertEqual(res["language"], "tr")
        self.assertIn("Kadıköy Estetik Diş", res["content"])
        self.assertIn("Kürşat", res["content"])
        self.assertIn("wa.me/905329998877", res["whatsapp_direct_url"])

    def test_generate_english_email_pitch(self):
        res = self.generator.generate_pitch(
            lead=self.lead,
            channel="email",
            tone="direct",
            lang="en",
            custom_sender_name="Alex",
            custom_agency_name="Apex Media"
        )
        self.assertEqual(res["channel"], "email")
        self.assertEqual(res["language"], "en")
        self.assertIn("Kadıköy Estetik Diş", res["content"])
        self.assertIn("Apex Media", res["content"])


if __name__ == "__main__":
    unittest.main()
