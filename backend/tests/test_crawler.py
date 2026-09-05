"""
Unit tests for WebsiteCrawler.
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.website_crawler import WebsiteCrawler, SimpleHTMLMetadataExtractor


class TestWebsiteCrawler(unittest.TestCase):
    def setUp(self):
        self.crawler = WebsiteCrawler()

    def test_clean_email_filters_junk_and_extensions(self):
        # Valid emails
        self.assertEqual(self.crawler._clean_email("info@dentistclinic.com"), "info@dentistclinic.com")
        self.assertEqual(self.crawler._clean_email("DR.AHMET@DISHEKIMI.COM"), "dr.ahmet@dishekimi.com")

        # False positives with image extensions
        self.assertIsNone(self.crawler._clean_email("logo@2x.png"))
        self.assertIsNone(self.crawler._clean_email("banner@3x.webp"))

        # Ignored infrastructure domains and placeholder emails
        self.assertIsNone(self.crawler._clean_email("user@example.com"))
        self.assertIsNone(self.crawler._clean_email("alert@sentry.io"))
        self.assertIsNone(self.crawler._clean_email("example@myfirm.com"))
        self.assertIsNone(self.crawler._clean_email("domain@company.com"))
        self.assertIsNone(self.crawler._clean_email("info@wix.com"))
        self.assertIsNone(self.crawler._clean_email("sentry@sentry-next.wixpress.com"))
        self.assertIsNone(self.crawler._clean_email("logo.png@business.com"))
        self.assertIsNone(self.crawler._clean_email("photo.jpg@agency.com"))
        self.assertIsNone(self.crawler._clean_email("test@domain.png"))

    def test_clean_phone_normalizes_turkish_mobile(self):
        self.assertEqual(self.crawler._clean_phone("0532 123 45 67"), "+90 532 123 45 67")
        self.assertEqual(self.crawler._clean_phone("5321234567"), "+90 532 123 45 67")
        self.assertEqual(self.crawler._clean_phone("+905321234567"), "+90 532 123 45 67")
        self.assertEqual(self.crawler._clean_phone("(0532) 123 45 67"), "+90 532 123 45 67")
        self.assertEqual(self.crawler._clean_phone("542 987 65 43"), "+90 542 987 65 43")
        self.assertEqual(self.crawler._clean_phone("+1 555 123 4567"), "+15551234567")

    def test_detect_whatsapp(self):
        links = ["https://instagram.com/clinic", "https://wa.me/905321234567"]
        phones = {"+90 532 123 45 67"}
        wa = self.crawler._detect_whatsapp(links, phones)
        self.assertEqual(wa, "https://wa.me/905321234567")

        # Automatically build wa.me from phones set if link missing
        wa_from_phone = self.crawler._detect_whatsapp([], {"+90 544 111 22 33"})
        self.assertEqual(wa_from_phone, "https://wa.me/905441112233")

        # International mobile WhatsApp
        wa_intl = self.crawler._detect_whatsapp([], {"+447911123456"})
        self.assertEqual(wa_intl, "https://wa.me/447911123456")

    def test_find_contact_urls_includes_all_required_slugs(self):
        links = [
            "/bize-ulasin", "/iletisim-bilgileri", "/contact-us",
            "/reach-us", "/impressum", "/kontakt", "/about-us"
        ]
        discovered = self.crawler._find_contact_urls(links, "https://example-biz.com")
        self.assertIn("https://example-biz.com/bize-ulasin", discovered)
        self.assertIn("https://example-biz.com/iletisim-bilgileri", discovered)
        self.assertIn("https://example-biz.com/contact-us", discovered)
        self.assertIn("https://example-biz.com/reach-us", discovered)
        self.assertIn("https://example-biz.com/impressum", discovered)
        self.assertIn("https://example-biz.com/kontakt", discovered)
        self.assertIn("https://example-biz.com/about-us", discovered)

    def test_html_parser_extracts_metadata(self):
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Kadıköy Elit Diş Polikliniği</title>
            <meta name="description" content="İmplant, ortodonti ve estetik gülüş tasarımı.">
        </head>
        <body>
            <a href="/iletisim">İletişim</a>
            <a href="mailto:info@elitdis.com">E-Posta Gönder</a>
            <p>Bizi arayın: 0532 555 12 34</p>
        </body>
        </html>
        """
        parser = SimpleHTMLMetadataExtractor()
        parser.feed(html)
        self.assertEqual(parser.title, "Kadıköy Elit Diş Polikliniği")
        self.assertEqual(parser.meta_description, "İmplant, ortodonti ve estetik gülüş tasarımı.")
        self.assertIn("mailto:info@elitdis.com", parser.links)


if __name__ == "__main__":
    unittest.main()
