"""
Unit tests for WebsiteCrawler.
"""
import unittest
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

        # Ignored infrastructure domains
        self.assertIsNone(self.crawler._clean_email("user@example.com"))
        self.assertIsNone(self.crawler._clean_email("alert@sentry.io"))

    def test_clean_phone_normalizes_turkish_mobile(self):
        self.assertEqual(self.crawler._clean_phone("0532 123 45 67"), "+90 532 123 45 67")
        self.assertEqual(self.crawler._clean_phone("5321234567"), "+90 532 123 45 67")
        self.assertEqual(self.crawler._clean_phone("+905321234567"), "+90 532 123 45 67")

    def test_detect_whatsapp(self):
        links = ["https://instagram.com/clinic", "https://wa.me/905321234567"]
        phones = {"+90 532 123 45 67"}
        wa = self.crawler._detect_whatsapp(links, phones)
        self.assertEqual(wa, "https://wa.me/905321234567")

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
