"""
Opportunity / Sales Gap Detector service for GeoLeads.
Analyzes leads for business vulnerabilities and provides high-converting sales pitch angles.
"""
from typing import List, Tuple
from app.models import Lead, SalesGap, OpportunitySeverity


class GapDetector:
    @staticmethod
    def analyze(lead: Lead) -> Tuple[int, List[SalesGap], str]:
        """
        Analyzes a Lead and returns:
        - opportunity_score (0 - 100)
        - list of SalesGap instances
        - primary_gap key
        """
        gaps: List[SalesGap] = []
        raw_score = 15  # Base lead score

        # 1. Check Missing Website
        if not lead.website or not lead.has_website:
            gaps.append(SalesGap(
                code="MISSING_WEBSITE",
                title="Web Sitesi Yok / Eksik",
                description="İşletmenin Google Maps haritasında web sitesi bulunmuyor. Müşteriler güvenilir bilgi veya hizmet detaylarına ulaşamıyor.",
                severity=OpportunitySeverity.HIGH,
                pitch_angle="Google Maps'te yüksek görünürlüğünüz var fakat bir web siteniz olmadığı için arayan potansiyel müşterilerin %73'ü rakiplerinize yöneliyor.",
                suggested_solution="Modern, mobil uyumlu ve SEO optimize kurumsal web sitesi & landing page kurulumu."
            ))
            raw_score += 35
        else:
            # 2. Check SSL Security if website exists
            if not lead.has_ssl:
                gaps.append(SalesGap(
                    code="NO_SSL_INSECURE",
                    title="Güvensiz Bağlantı (SSL Eksik)",
                    description="Web sitesi HTTPS desteklemiyor veya SSL sertifikası hatalı. Tarayıcılarda 'Güvenli Değil' uyarısı çıkıyor.",
                    severity=OpportunitySeverity.MEDIUM,
                    pitch_angle="Web sitenize giren ziyaretçiler 'Güvenli Değil' uyarısıyla karşılaşıyor. Bu durum satış ve form dönüşümlerini anında %80 düşürür.",
                    suggested_solution="SSL sertifikası kurulumu, HTTPS yönlendirmesi ve güvenlik optimizasyonu."
                ))
                raw_score += 20

            # 3. Check Social Media Presence
            has_socials = bool(lead.instagram or lead.facebook or lead.linkedin or lead.twitter)
            if not has_socials:
                gaps.append(SalesGap(
                    code="NO_SOCIAL_MEDIA",
                    title="Sosyal Medya Varlığı Eksik",
                    description="Web sitesinde veya profilde Instagram, Facebook veya LinkedIn bağlantısı tespit edilemedi.",
                    severity=OpportunitySeverity.MEDIUM,
                    pitch_angle="Sektörünüzde potansiyel müşteriler son işlerinizi ve referanslarınızı Instagram'da görmek ister. Sosyal medya eksikliği güven kaybı yaratır.",
                    suggested_solution="Sosyal medya hesap kurulumu, marka kimliği ve içerik yönetim paketi."
                ))
                raw_score += 15

        # 4. Check Google Reviews and Rating
        if lead.rating is not None:
            if lead.rating < 4.2:
                gaps.append(SalesGap(
                    code="LOW_RATING",
                    title=f"Düşük Google Puanı ({lead.rating}/5.0)",
                    description=f"İşletmenin Google puanı {lead.rating}. 4.2'nin altındaki işletmeler yerel aramalarda geri plana düşer.",
                    severity=OpportunitySeverity.HIGH,
                    pitch_angle=f"Google puanınız şu anda {lead.rating}. Müşteriler genellikle 4.5 üzeri rakipleri tercih eder. Olumsuz yorumları telafi edip puanınızı yükseltebiliriz.",
                    suggested_solution="Google Yorum & İtibar Yönetimi (NFC kartlar, QR yorum sistemi, memnuniyet anketleri)."
                ))
                raw_score += 25
            elif lead.review_count < 15:
                gaps.append(SalesGap(
                    code="FEW_REVIEWS",
                    title=f"Yetersiz Yorum Sayısı ({lead.review_count} Yorum)",
                    description=f"Toplam yalnızca {lead.review_count} yorum var. Bölgedeki rakiplerin çok gerisinde.",
                    severity=OpportunitySeverity.MEDIUM,
                    pitch_angle=f"Haritada yalnızca {lead.review_count} yorumunuz var. Bölgenizde ilk 3'e çıkmak ve güven inşa etmek için aktif yorum toplama stratejisi şart.",
                    suggested_solution="Yerel SEO ve Google Harita organik sıralama yükseltme çalışması."
                ))
                raw_score += 20
        elif lead.review_count == 0:
            gaps.append(SalesGap(
                code="ZERO_REVIEWS",
                title="Henüz Hiç Google Yorumu Yok",
                description="Profilde hiç kullanıcı değerlendirmesi yok. Müşteriler çekimser kalıyor.",
                severity=OpportunitySeverity.HIGH,
                pitch_angle="Google profilinizde henüz yorum bulunmuyor. Yeni müşteriler ilk izlenimde yorumu olan firmaları seçer.",
                suggested_solution="Hızlı başlangıç yorum kampanyası ve yerel müşteri referans sistemi."
            ))
            raw_score += 25

        # 5. Check WhatsApp Quick Contact
        if not lead.whatsapp:
            gaps.append(SalesGap(
                code="NO_WHATSAPP_CONVERSION",
                title="Hızlı WhatsApp İletişim Hattı Yok",
                description="Müşterilerin doğrudan tek tıkla mesaj atabileceği WhatsApp bağlantısı yok.",
                severity=OpportunitySeverity.LOW,
                pitch_angle="Ziyaretçiler artık telefon araması yapmak yerine WhatsApp'tan hızlı fiyat ve bilgi sormayı tercih ediyor. WhatsApp butonu ekleyerek potansiyel müşteri kaybını önleyelim.",
                suggested_solution="Web sitesine ve profile 1-tıkla WhatsApp akıllı mesajlaşma butonu ve otomatik karşılama botu."
            ))
            raw_score += 15

        # Normalize score between 10 and 100
        final_score = min(100, max(15, raw_score))

        # Determine primary gap
        primary_gap = gaps[0].code if gaps else "GENERAL_DIGITAL_GROWTH"

        return final_score, gaps, primary_gap


gap_detector = GapDetector()
