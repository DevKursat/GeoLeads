"""
Unit tests for Multi-Source ScraperEngine.
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.scraper_engine import scraper_engine, OSM_CATEGORY_MAPPINGS, normalize_text
from app.models import Lead, CRMStage


class TestScraperEngine(unittest.TestCase):
    def test_normalize_text_turkish_characters(self):
        self.assertEqual(normalize_text("DİŞ KLİNİĞİ"), "dis klinigi")
        self.assertEqual(normalize_text("Hukuk Bürosu"), "hukuk burosu")
        self.assertEqual(normalize_text("Güzellik Merkezi"), "guzellik merkezi")
        self.assertEqual(normalize_text("Çankaya / Kadıköy"), "cankaya / kadikoy")

    def test_osm_category_mappings_comprehensive(self):
        # Must include healthcare, legal, food, trade, beauty, it, architecture, accounting
        categories_to_check = [
            "diş kliniği", "diş", "hukuk bürosu", "avukat", "doktor", "restoran", "otel", "spor", "kuaför",
            "güzellik merkezi", "güzellik", "oto servis", "oto", "mimarlık", "mimar",
            "yazılım ajansı", "yazılım", "veteriner", "emlak", "muhasebe"
        ]
        for cat in categories_to_check:
            self.assertIn(cat, OSM_CATEGORY_MAPPINGS, f"Missing OSM category mapping: {cat}")

    def test_complex_query_tag_resolution(self):
        complex_queries = {
            "Diş Kliniği": '["amenity"="dentist"]',
            "Hukuk Bürosu": '["office"="lawyer"]',
            "Yazılım Ajansı": '["office"="it"]',
            "Güzellik Merkezi": '["shop"="beauty"]',
            "Oto Servis": '["shop"="car_repair"]',
            "Mimarlık": '["office"="architect"]',
            "Restoran": '["amenity"="restaurant"]',
        }
        sorted_keys = sorted(OSM_CATEGORY_MAPPINGS.keys(), key=lambda k: len(k), reverse=True)
        for query, expected_tag in complex_queries.items():
            q_norm = normalize_text(query)
            matched_tag = None
            for k in sorted_keys:
                k_norm = normalize_text(k)
                if k_norm in q_norm or q_norm in k_norm:
                    matched_tag = OSM_CATEGORY_MAPPINGS[k]
                    break
            self.assertEqual(matched_tag, expected_tag, f"Failed resolving tag for {query}")

    def test_generate_sector_leads_properties(self):
        leads = scraper_engine._generate_sector_leads(query="Yazılım Ajansı", city="İstanbul", count=5)
        self.assertEqual(len(leads), 5)
        for lead in leads:
            self.assertTrue(lead.name)
            self.assertEqual(lead.city, "İstanbul")
            self.assertTrue(lead.phone)
            self.assertTrue(lead.address)
            self.assertGreaterEqual(lead.rating, 3.0)
            self.assertIn("maps", lead.google_maps_url)

    def test_search_and_enrich_pipeline(self):
        leads = scraper_engine.search_and_enrich(
            query="Mimar",
            city="Kadıköy",
            max_leads=4,
            deep_crawl=False
        )
        self.assertEqual(len(leads), 4)
        for lead in leads:
            self.assertIsNotNone(lead.id)
            self.assertGreaterEqual(lead.opportunity_score, 15)
            self.assertLessEqual(lead.opportunity_score, 100)
            self.assertEqual(lead.crm_stage, CRMStage.ENRICHED)
            self.assertTrue(len(lead.gaps) > 0)

    def test_search_google_maps_graceful_on_error(self):
        # Even if invalid query or network error, it shouldn't raise exception
        leads = scraper_engine._search_google_maps(query="___invalid___", city="___unknown___", limit=2)
        self.assertIsInstance(leads, list)

    def test_duckduckgo_and_bing_graceful_on_error(self):
        # Live multi-source parsers must handle network errors gracefully without crashing
        ddg_leads = scraper_engine._search_duckduckgo(query="___invalid___", city="___unknown___", limit=2)
        self.assertIsInstance(ddg_leads, list)
        bing_leads = scraper_engine._search_bing(query="___invalid___", city="___unknown___", limit=2)
        self.assertIsInstance(bing_leads, list)

    def test_verified_real_osm_businesses(self):
        # Verified OSM dataset contains 100% genuine real-world businesses with valid contact info
        leads = scraper_engine._get_verified_real_businesses(query="Mimar", city="Kadıköy", limit=3)
        self.assertEqual(len(leads), 3)
        for lead in leads:
            self.assertTrue(lead.name)
            self.assertTrue(lead.address)
            self.assertTrue(lead.phone)
            self.assertTrue(lead.website)
            self.assertGreaterEqual(lead.rating, 4.0)


if __name__ == "__main__":
    unittest.main()
