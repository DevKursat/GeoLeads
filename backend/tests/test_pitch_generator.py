"""
Unit tests for AI Pitch Generator.
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

    def test_edge_case_lead_missing_optional_fields(self):
        bare_lead = Lead(name="", city="")
        res = self.generator.generate_pitch(bare_lead)
        self.assertIsNotNone(res["content"])
        self.assertEqual(res["whatsapp_direct_url"], "")

    def test_openai_and_ollama_fallback_gracefully(self):
        self.generator.provider = "openai"
        res = self.generator.generate_pitch(self.lead)
        self.assertIsNotNone(res["content"])

        self.generator.provider = "ollama"
        res2 = self.generator.generate_pitch(self.lead)
        self.assertIsNotNone(res2["content"])

    def test_hair_dye_wholesale_pitch_turkish_and_english(self):
        # Hair Dye pitch for hair salons: checks wholesale hair dye, salon supplies, and sample trial
        res_tr = self.generator.generate_pitch(
            lead=self.lead,
            channel="whatsapp",
            tone="friendly",
            lang="tr",
            product_pitch_type="hair_dye"
        )
        self.assertIn("saç boyası", res_tr["content"].lower())
        self.assertIn("numune", res_tr["content"].lower())
        self.assertEqual(res_tr["product_pitch_type"], "hair_dye")

        res_en = self.generator.generate_pitch(
            lead=self.lead,
            channel="email",
            tone="consultative",
            lang="en",
            product_pitch_type="hair_dye"
        )
        self.assertIn("hair dye", res_en["content"].lower())
        self.assertIn("wholesale", res_en["content"].lower())
        self.assertIn("sample", res_en["content"].lower())

    def test_steam_iron_silter_pitch_turkish_and_english(self):
        # Industrial steam iron & Silter boiler installation pitch for textile workshops
        textile_lead = Lead(
            name="Merter Dikim ve Tekstil Atölyesi",
            category="Tekstil",
            city="Güngören",
            phone="+90 533 111 22 33",
            whatsapp="https://wa.me/905331112233"
        )
        res_tr = self.generator.generate_pitch(
            lead=textile_lead,
            channel="whatsapp",
            tone="consultative",
            lang="tr",
            product_pitch_type="steam_iron"
        )
        self.assertIn("silter", res_tr["content"].lower())
        self.assertIn("ütü", res_tr["content"].lower())
        self.assertIn("tesisat", res_tr["content"].lower())

        res_en = self.generator.generate_pitch(
            lead=textile_lead,
            channel="email",
            tone="urgency",
            lang="en",
            product_pitch_type="steam_iron"
        )
        self.assertIn("steam iron", res_en["content"].lower())
        self.assertIn("boiler", res_en["content"].lower())

    def test_software_pitch_turkish_and_english(self):
        # Software & web solution pitch for businesses
        res_tr = self.generator.generate_pitch(
            lead=self.lead,
            channel="whatsapp",
            tone="direct",
            lang="tr",
            product_pitch_type="software"
        )
        self.assertIn("yazılım", res_tr["content"].lower())
        self.assertIn("otomasyon", res_tr["content"].lower())

        res_en = self.generator.generate_pitch(
            lead=self.lead,
            channel="email",
            tone="friendly",
            lang="en",
            product_pitch_type="software"
        )
        self.assertIn("software", res_en["content"].lower())
        self.assertIn("demo", res_en["content"].lower())

    def test_custom_product_pitch_turkish_and_english(self):
        # Custom product input: embeds custom product accurately
        res_tr = self.generator.generate_pitch(
            lead=self.lead,
            channel="whatsapp",
            tone="consultative",
            lang="tr",
            product_pitch_type="custom",
            product_name="Güneş Paneli Sistemleri"
        )
        self.assertIn("Güneş Paneli Sistemleri", res_tr["content"])
        self.assertIn("Güneş Paneli Sistemleri", res_tr["subject"])
        self.assertEqual(res_tr["product_name"], "Güneş Paneli Sistemleri")

        res_en = self.generator.generate_pitch(
            lead=self.lead,
            channel="email",
            tone="consultative",
            lang="en",
            product_pitch_type="custom",
            product_name="Organic Olive Oil"
        )
        self.assertIn("Organic Olive Oil", res_en["content"])
        self.assertIn("Organic Olive Oil", res_en["subject"])

    def test_multi_step_sequence_followup_and_breakup(self):
        # Step 2: Follow-up 1 (Case Study & Social Proof)
        res_step2_tr = self.generator.generate_pitch(
            lead=self.lead,
            channel="whatsapp",
            product_pitch_type="hair_dye",
            sequence_step=2
        )
        self.assertEqual(res_step2_tr["sequence_step"], 2)
        self.assertIn("vaka çalışması", res_step2_tr["content"].lower())
        self.assertIn("tester", res_step2_tr["content"].lower())

        res_step2_iron = self.generator.generate_pitch(
            lead=self.lead,
            channel="email",
            product_pitch_type="steam_iron",
            sequence_step=2
        )
        self.assertIn("buhar", res_step2_iron["content"].lower())
        self.assertIn("silter", res_step2_iron["content"].lower())

        res_step2_sw = self.generator.generate_pitch(
            lead=self.lead,
            channel="whatsapp",
            product_pitch_type="software",
            sequence_step=2
        )
        self.assertIn("demo", res_step2_sw["content"].lower())

        # Step 3: Follow-up 2 (Respectful Break-up / File Close)
        res_step3_tr = self.generator.generate_pitch(
            lead=self.lead,
            channel="whatsapp",
            product_pitch_type="hair_dye",
            sequence_step=3
        )
        self.assertEqual(res_step3_tr["sequence_step"], 3)
        self.assertIn("arşive kaldırıyorum", res_step3_tr["content"].lower())
        self.assertIn("kapatıyorum", res_step3_tr["subject"].lower())

        res_step3_iron = self.generator.generate_pitch(
            lead=self.lead,
            channel="email",
            product_pitch_type="steam_iron",
            sequence_step=3
        )
        self.assertIn("dosyanızı kapatıyorum", res_step3_iron["content"].lower())
        self.assertIn("arşive kaldırıyorum", res_step3_iron["subject"].lower())

        # Step 2 and 3 English
        res_step2_en = self.generator.generate_pitch(
            lead=self.lead,
            channel="whatsapp",
            lang="en",
            sequence_step=2
        )
        self.assertIn("following up", res_step2_en["content"].lower())

        res_step3_en = self.generator.generate_pitch(
            lead=self.lead,
            channel="email",
            lang="en",
            sequence_step=3
        )
        self.assertIn("closing your file", res_step3_en["content"].lower())
        self.assertIn("closing out your file", res_step3_en["subject"].lower())

    def test_roi_metrics_injection(self):
        roi = {
            "deal_value": "15.000 TL",
            "payback_days": "45",
            "roi_percent": "180"
        }
        res_tr = self.generator.generate_pitch(
            lead=self.lead,
            channel="whatsapp",
            lang="tr",
            roi_metrics=roi
        )
        self.assertIn("Finansal ROI Analizi", res_tr["content"])
        self.assertIn("15.000 TL", res_tr["content"])
        self.assertIn("45 günde", res_tr["content"])
        self.assertIn("%180", res_tr["content"])
        self.assertIn("wa.me/905329998877", res_tr["whatsapp_direct_url"])

        res_en = self.generator.generate_pitch(
            lead=self.lead,
            channel="email",
            lang="en",
            roi_metrics=roi
        )
        self.assertIn("Financial ROI Analysis", res_en["content"])
        self.assertIn("15.000 TL", res_en["content"])
        self.assertIn("180% ROI", res_en["content"])


if __name__ == "__main__":
    unittest.main()

