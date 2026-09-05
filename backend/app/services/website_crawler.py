"""
Website deep crawler service for GeoLeads.
Extracts verified emails, phones, WhatsApp links, social media handles,
page metadata, and SSL security status with zero external dependencies.
"""
import re
import ssl
import urllib.request
import urllib.parse
from html.parser import HTMLParser
from typing import Dict, List, Optional, Set, Tuple
from app.core.config import CRAWLER_TIMEOUT_SECONDS, CRAWLER_USER_AGENT

# Common email false positives & junk domains
EMAIL_BLACKLIST_EXTENSIONS = (
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp', '.ico',
    '.tiff', '.css', '.js', '.woff', '.woff2', '.ttf', '.mp4', '.pdf',
    '.zip', '.rar', '.exe', '.apk'
)
IGNORED_EMAIL_DOMAINS = (
    'example.com', 'domain.com', 'email.com', 'sentry.io', 'wixpress.com',
    'wix.com', 'sentry-next.wixpress.com', 'schema.org', 'w3.org', 'google.com',
    'googleapis.com', 'wordpress.org', 'wordpress.com', 'cloudflare.com',
    'bootstrap.com', 'fontawesome.com', 'jquery.com', 'mysite.com',
    'yoursite.com', 'sample.com', 'github.com', 'gravatar.com'
)
IGNORED_EMAIL_PREFIXES = (
    'example', 'domain', 'email', 'yourname', 'test', 'sample', 'user',
    'name', 'sentry', 'mailer', 'noreply', 'no-reply', 'postmaster', 'webmaster'
)

# Regex Patterns
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
TURKISH_PHONE_REGEX = re.compile(
    r'(?:(?:\+?90|0)?[\s.-]?)?\(?(?:0?5[0-9]{2}|0?[2-489][0-9]{2})\)?[\s.-]?[0-9]{3}[\s.-]?[0-9]{2}[\s.-]?[0-9]{2}'
)
INTL_PHONE_REGEX = re.compile(
    r'\+(?:[1-9]\d{0,2})[\s.-]?\(?\d{1,4}\)?[\s.-]?\d{2,4}[\s.-]?\d{2,4}(?:[\s.-]?\d{2,4})?'
)

# Subpages to discover contact information
CONTACT_PAGE_SLUGS = [
    '/bize-ulasin', '/bizeulasin', '/bize_ulasin',
    '/iletisim-bilgileri', '/iletisimbilgileri', '/iletisim',
    '/contact-us', '/contact', '/reach-us', '/reach_us',
    '/impressum', '/kontakt', '/kunye',
    '/about-us', '/about', '/hakkimizda',
    '/iletisim/', '/contact-us/', '/bize-ulasin/', '/kontakt/',
    '/contact/', '/about-us/', '/hakkimizda/'
]


class SimpleHTMLMetadataExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title: str = ""
        self.in_title: bool = False
        self.meta_description: str = ""
        self.links: List[str] = []
        self.text_chunks: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        attr_dict = {k.lower(): (v or "") for k, v in attrs}

        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            name = attr_dict.get("name", "").lower()
            prop = attr_dict.get("property", "").lower()
            if name == "description" or prop == "og:description":
                if not self.meta_description:
                    self.meta_description = attr_dict.get("content", "").strip()
        elif tag == "a":
            href = attr_dict.get("href", "").strip()
            if href:
                self.links.append(href)

    def handle_endtag(self, tag: str):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str):
        if self.in_title:
            self.title += data
        clean = data.strip()
        if clean:
            self.text_chunks.append(clean)


class WebsiteCrawler:
    def __init__(self, timeout: int = CRAWLER_TIMEOUT_SECONDS):
        self.timeout = timeout
        # Create relaxed SSL context for inspecting misconfigured or self-signed sites
        self.ssl_ctx = ssl.create_default_context()
        self.ssl_ctx.check_hostname = False
        self.ssl_ctx.verify_mode = ssl.CERT_NONE

    def crawl(self, website_url: str) -> Dict[str, any]:
        """
        Deep crawls website homepage + discovered contact pages.
        Returns extracted emails, phones, social links, SSL status, and meta tags.
        """
        if not website_url:
            return self._empty_result()

        # Normalize URL
        url = website_url.strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        has_ssl = False
        parsed_url = urllib.parse.urlparse(url)
        base_origin = f"{parsed_url.scheme}://{parsed_url.netloc}"

        emails: Set[str] = set()
        phones: Set[str] = set()
        whatsapp: str = ""
        social_links = {
            "instagram": "",
            "facebook": "",
            "linkedin": "",
            "twitter": "",
            "youtube": ""
        }
        meta_title = ""
        meta_description = ""

        # 1. Fetch homepage
        html_content, status_code, is_ssl = self._fetch_url(url)
        has_ssl = is_ssl

        if not html_content and url.startswith("https://"):
            # Fallback to http if https failed
            http_url = "http://" + url[8:]
            html_content, status_code, _ = self._fetch_url(http_url)

        if not html_content:
            return {
                "has_website": False,
                "has_ssl": False,
                "emails": [],
                "phones": [],
                "whatsapp": "",
                "instagram": "",
                "facebook": "",
                "linkedin": "",
                "twitter": "",
                "youtube": "",
                "meta_title": "",
                "meta_description": ""
            }

        # Parse Homepage HTML
        parser = SimpleHTMLMetadataExtractor()
        try:
            parser.feed(html_content)
            meta_title = parser.title.strip()[:180]
            meta_description = parser.meta_description.strip()[:300]
        except Exception:
            pass

        # Extract contact data from homepage
        self._extract_from_text_and_links(
            html_content, parser.links, emails, phones, social_links
        )

        # 2. If emails or phones not found, deep search contact pages
        if len(emails) == 0 or len(phones) == 0:
            contact_candidate_urls = self._find_contact_urls(parser.links, base_origin)
            for sub_url in contact_candidate_urls[:3]:  # max 3 subpages to keep it blazing fast
                sub_html, _, _ = self._fetch_url(sub_url)
                if sub_html:
                    sub_parser = SimpleHTMLMetadataExtractor()
                    try:
                        sub_parser.feed(sub_html)
                    except Exception:
                        pass
                    self._extract_from_text_and_links(
                        sub_html, sub_parser.links, emails, phones, social_links
                    )
                    if len(emails) > 0 and len(phones) > 0:
                        break

        # WhatsApp detection
        whatsapp = self._detect_whatsapp(parser.links, phones)

        return {
            "has_website": True,
            "has_ssl": has_ssl,
            "emails": sorted(list(emails)),
            "phones": sorted(list(phones)),
            "whatsapp": whatsapp,
            "instagram": social_links["instagram"],
            "facebook": social_links["facebook"],
            "linkedin": social_links["linkedin"],
            "twitter": social_links["twitter"],
            "youtube": social_links["youtube"],
            "meta_title": meta_title,
            "meta_description": meta_description
        }

    def _fetch_url(self, url: str) -> Tuple[str, int, bool]:
        """Fetches URL and returns (content, status_code, has_ssl)"""
        headers = {
            "User-Agent": CRAWLER_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        req = urllib.request.Request(url, headers=headers)
        is_ssl = url.startswith("https://")

        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=self.ssl_ctx) as response:
                content = response.read()
                # Determine charset
                charset = "utf-8"
                content_type = response.headers.get("content-type", "")
                if "charset=" in content_type.lower():
                    charset = content_type.lower().split("charset=")[-1].split(";")[0].strip()
                try:
                    text = content.decode(charset, errors="ignore")
                except Exception:
                    text = content.decode("utf-8", errors="ignore")
                return text, response.status, is_ssl
        except urllib.error.HTTPError as e:
            return "", e.code, is_ssl
        except Exception:
            return "", 0, False

    def _extract_from_text_and_links(
        self,
        html_text: str,
        links: List[str],
        emails: Set[str],
        phones: Set[str],
        social_links: Dict[str, str]
    ):
        # 1. Emails via regex
        for raw_email in EMAIL_REGEX.findall(html_text):
            cleaned = self._clean_email(raw_email)
            if cleaned:
                emails.add(cleaned)

        # 2. Links scanning (mailto, tel, socials)
        for link in links:
            lower = link.lower().strip()
            # mailto:
            if lower.startswith("mailto:"):
                email_part = lower.replace("mailto:", "").split("?")[0].strip()
                cleaned = self._clean_email(email_part)
                if cleaned:
                    emails.add(cleaned)
            # tel:
            elif lower.startswith("tel:"):
                phone_part = lower.replace("tel:", "").strip()
                cleaned = self._clean_phone(phone_part)
                if cleaned:
                    phones.add(cleaned)
            # Social links
            elif "instagram.com/" in lower and not social_links["instagram"]:
                if not any(x in lower for x in ["/p/", "/reel/", "/explore/", "instagram.com/accounts"]):
                    social_links["instagram"] = link
            elif "facebook.com/" in lower and not social_links["facebook"]:
                if not any(x in lower for x in ["/sharer", "/share", "/dialog", "facebook.com/policies"]):
                    social_links["facebook"] = link
            elif "linkedin.com/" in lower and not social_links["linkedin"]:
                if "linkedin.com/company/" in lower or "linkedin.com/in/" in lower:
                    social_links["linkedin"] = link
            elif ("twitter.com/" in lower or "x.com/" in lower) and not social_links["twitter"]:
                if not any(x in lower for x in ["/intent/", "/share"]):
                    social_links["twitter"] = link
            elif "youtube.com/" in lower and not social_links["youtube"]:
                social_links["youtube"] = link

        # 3. Turkish and International phone detection in body
        for match in TURKISH_PHONE_REGEX.finditer(html_text):
            full_match = match.group(0).strip()
            # Must look like a realistic phone number
            digits = re.sub(r'\D', '', full_match)
            if 10 <= len(digits) <= 12:
                formatted = self._clean_phone(full_match)
                if formatted:
                    phones.add(formatted)

        for match in INTL_PHONE_REGEX.finditer(html_text):
            full_match = match.group(0).strip()
            digits = re.sub(r'\D', '', full_match)
            if 10 <= len(digits) <= 15:
                formatted = self._clean_phone(full_match)
                if formatted:
                    phones.add(formatted)

    def _clean_email(self, email: str) -> Optional[str]:
        if not email or "@" not in email:
            return None
        e = email.lower().strip().strip(".'\"<>[]()\\/,;: ")
        if len(e) < 6 or len(e) > 80:
            return None
        # Check overall blacklist extensions
        if any(e.endswith(ext) for ext in EMAIL_BLACKLIST_EXTENSIONS):
            return None
        parts = e.split("@")
        if len(parts) != 2:
            return None
        local_part, domain = parts[0], parts[1]

        # Check local part for image extensions (e.g. logo.png@..., pic.jpg@...)
        if any(local_part.endswith(ext) for ext in EMAIL_BLACKLIST_EXTENSIONS):
            return None
        if re.search(r'\.(?:png|jpg|jpeg|gif|svg|webp|bmp|ico|css|js|pdf|mp4)$', local_part):
            return None

        # Check placeholder local parts & common junk prefixes
        if local_part in IGNORED_EMAIL_PREFIXES:
            return None
        if any(local_part.startswith(p + "_") or local_part.startswith(p + ".") for p in IGNORED_EMAIL_PREFIXES):
            return None
        if local_part.startswith("sentry-") or local_part.startswith("wix-"):
            return None

        # Check domain structure
        if not domain or "." not in domain:
            return None
        if domain.startswith("-") or domain.endswith("-") or domain.startswith("."):
            return None

        # Check ignored domains or subdomains
        if domain in IGNORED_EMAIL_DOMAINS or any(domain.endswith("." + d) for d in IGNORED_EMAIL_DOMAINS):
            return None

        # Reject invalid TLDs (e.g., test@domain.png, test@site.jpg)
        tld = domain.split(".")[-1]
        if f".{tld}" in EMAIL_BLACKLIST_EXTENSIONS or not re.match(r'^[a-z]{2,12}$', tld):
            return None

        return e

    def _clean_phone(self, phone_str: str) -> Optional[str]:
        if not phone_str:
            return None
        clean_input = phone_str.strip()
        digits = re.sub(r'\D', '', clean_input)

        # 1. Turkish Mobile numbers (05xx, +90 5xx, 5xx, (05xx), (5xx))
        if len(digits) == 10 and digits.startswith("5"):
            return f"+90 {digits[0:3]} {digits[3:6]} {digits[6:8]} {digits[8:10]}"
        elif len(digits) == 11 and digits.startswith("05"):
            return f"+90 {digits[1:4]} {digits[4:7]} {digits[7:9]} {digits[9:11]}"
        elif len(digits) == 12 and digits.startswith("905"):
            return f"+90 {digits[2:5]} {digits[5:8]} {digits[8:10]} {digits[10:12]}"
        elif len(digits) == 14 and digits.startswith("00905"):
            return f"+90 {digits[4:7]} {digits[7:10]} {digits[10:12]} {digits[12:14]}"

        # 2. Turkish Landlines (02xx, 03xx, 04xx)
        if len(digits) == 10 and digits[0] in "234":
            return f"+90 ({digits[0:3]}) {digits[3:6]} {digits[6:8]} {digits[8:10]}"
        elif len(digits) == 11 and digits.startswith("0") and digits[1] in "234":
            return f"+90 ({digits[1:4]}) {digits[4:7]} {digits[7:9]} {digits[9:11]}"
        elif len(digits) == 12 and digits.startswith("90") and digits[2] in "234":
            return f"+90 ({digits[2:5]}) {digits[5:8]} {digits[8:10]} {digits[10:12]}"

        # 3. International Mobile / Phone formats
        if clean_input.startswith("+") and 10 <= len(digits) <= 15:
            return f"+{digits}"
        elif len(digits) >= 10:
            return clean_input

        return None

    def _detect_whatsapp(self, links: List[str], phones: Set[str]) -> str:
        # Check direct WhatsApp links
        for link in links:
            if "wa.me/" in link or "api.whatsapp.com/send" in link or "whatsapp://" in link:
                return link

        # If any phone number is mobile, construct wa.me link
        for p in sorted(list(phones)):
            digits = re.sub(r'\D', '', p)
            if digits.startswith("905") and len(digits) == 12:
                return f"https://wa.me/{digits}"
            elif digits.startswith("05") and len(digits) == 11:
                return f"https://wa.me/9{digits}"
            elif digits.startswith("5") and len(digits) == 10:
                return f"https://wa.me/90{digits}"
            elif p.startswith("+") and not p.startswith("+90 (2") and not p.startswith("+90 (3") and not p.startswith("+90 (4"):
                if 10 <= len(digits) <= 15 and not digits.startswith("902") and not digits.startswith("903") and not digits.startswith("904"):
                    return f"https://wa.me/{digits}"
        return ""

    def _find_contact_urls(self, links: List[str], base_origin: str) -> List[str]:
        discovered = []
        for link in links:
            for slug in CONTACT_PAGE_SLUGS:
                if slug in link.lower():
                    full_url = urllib.parse.urljoin(base_origin, link)
                    if full_url not in discovered and full_url.startswith(base_origin):
                        discovered.append(full_url)
        # Also add default prioritized slugs if not found
        prioritized_slugs = [
            '/bize-ulasin', '/iletisim-bilgileri', '/iletisim',
            '/contact-us', '/reach-us', '/impressum', '/kontakt', '/about-us'
        ]
        for slug in prioritized_slugs:
            fallback_url = f"{base_origin.rstrip('/')}{slug}"
            if fallback_url not in discovered:
                discovered.append(fallback_url)
        return discovered

    def _empty_result(self) -> Dict[str, any]:
        return {
            "has_website": False,
            "has_ssl": False,
            "emails": [],
            "phones": [],
            "whatsapp": "",
            "instagram": "",
            "facebook": "",
            "linkedin": "",
            "twitter": "",
            "youtube": "",
            "meta_title": "",
            "meta_description": ""
        }


crawler = WebsiteCrawler()
