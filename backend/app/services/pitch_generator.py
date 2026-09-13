"""
AI Personalized Pitch Generator for GeoLeads.
Generates high-converting Cold Emails and WhatsApp Pitches tailored
to each business's specific gaps, category, city, and metrics.
Supports Gemini, OpenAI, Ollama, and high-converting built-in offline templates.
"""
import json
import ssl
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional
from app.core.config import (
    AI_PROVIDER, GEMINI_API_KEY, OPENAI_API_KEY, OLLAMA_BASE_URL
)
from app.models import Lead


class PitchGenerator:
    def __init__(self):
        self.provider = AI_PROVIDER

    def generate_pitch(
        self,
        lead: Lead,
        channel: str = "whatsapp",     # 'whatsapp' or 'email'
        tone: str = "consultative",    # 'direct', 'consultative', 'growth'
        lang: str = "tr",              # 'tr' or 'en'
        custom_sender_name: str = "Kürşat",
        custom_agency_name: str = "Dijital Büyüme Ajansı",
        product_pitch_type: str = "general", # 'software' | 'hair_dye' | 'steam_iron' | 'custom' | 'general'
        product_name: str = "",
        sequence_step: int = 1,        # 1: Initial Hook, 2: Day 3 Follow-up, 3: Day 7 Break-up Call
        roi_metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generates personalized sales pitch.
        First attempts external AI if configured, otherwise uses built-in high-converting templates.
        Supports general digital audits, software, hair dye/cosmetics wholesale, industrial steam irons & Silter, and custom products.
        """
        # Normalize pitch type
        p_type = (product_pitch_type or "general").strip().lower()
        p_name = (product_name or "").strip()

        # Attempt AI provider if configured
        if self.provider == "gemini" and GEMINI_API_KEY:
            try:
                res = self._generate_gemini(lead, channel, tone, lang, custom_sender_name, custom_agency_name, p_type, p_name)
                if res:
                    return res
            except Exception:
                pass
        elif self.provider == "openai" and OPENAI_API_KEY:
            try:
                res = self._generate_openai(lead, channel, tone, lang, custom_sender_name, custom_agency_name, p_type, p_name)
                if res:
                    return res
            except Exception:
                pass
        elif self.provider == "ollama":
            try:
                res = self._generate_ollama(lead, channel, tone, lang, custom_sender_name, custom_agency_name, p_type, p_name)
                if res:
                    return res
            except Exception:
                pass

        # High-converting offline template engine (100% reliable, zero external API key required)
        return self._generate_template(
            lead, channel, tone, lang, custom_sender_name, custom_agency_name,
            p_type, p_name, sequence_step=sequence_step, roi_metrics=roi_metrics
        )

    def _generate_template(
        self,
        lead: Lead,
        channel: str,
        tone: str,
        lang: str,
        sender: str,
        agency: str,
        product_pitch_type: str = "general",
        product_name: str = "",
        sequence_step: int = 1,
        roi_metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        biz_name = lead.name or "İşletme Yetkilisi"
        city = lead.city or "bölgenizdeki"
        category = lead.category or "sektör"
        rating_str = f"{lead.rating}★ ({lead.review_count} yorum)" if lead.rating else "yeni profil"
        tone_lower = (tone or "consultative").lower()
        p_type = (product_pitch_type or "general").strip().lower()

        # 0. Multi-Step Outreach Sequence Handling (Step 2: Follow-up, Step 3: Break-up)
        if sequence_step in (2, 3):
            subject, message = self._build_sequence_pitch(
                lead=lead,
                p_type=p_type,
                product_name=product_name,
                channel=channel,
                tone_lower=tone_lower,
                lang=lang,
                sender=sender,
                agency=agency,
                step=sequence_step
            )
        # 1. Product-Tailored Pitch Modes
        elif p_type in ("hair_dye", "steam_iron", "software", "custom"):
            subject, message = self._build_product_pitch_content(
                lead=lead,
                p_type=p_type,
                product_name=product_name,
                channel=channel,
                tone_lower=tone_lower,
                lang=lang,
                sender=sender,
                agency=agency
            )
        else:
            # 2. General Gap-Based Pitch Mode
            gap_hooks_tr = {
                "MISSING_WEBSITE": {
                    "hook": f"Google Haritalar'da {biz_name} profilinizi inceledim. Harika bir konumdasınız ancak resmi bir web siteniz olmadığı için arayan müşterilerin çoğu rakiplerinize geçiyor.",
                    "solution": "48 saat içinde mobil uyumlu, randevu/sipariş butonlu profesyonel bir web sitesi hazırlayabiliriz.",
                    "cta": "Örnek bir taslak tasarımı size WhatsApp'tan ücretsiz iletmemi ister misiniz?"
                },
                "NO_SSL_INSECURE": {
                    "hook": f"{biz_name} web sitenizi incelerken Chrome tarayıcısında 'Güvenli Değil' uyarısı çıktığını fark ettim. Bu durum ziyaretçilerin %82'sinin siteyi terk etmesine sebep oluyor.",
                    "solution": "Web sitenize SSL güvenlik sertifikası kurup tüm güvenlik açıklarını 1 gün içinde çözebiliriz.",
                    "cta": "Hızlı bir güvenlik raporunu incelemeniz için paylaşabilir miyim?"
                },
                "LOW_RATING": {
                    "hook": f"{city} bölgesinde {category} aramasında profilinizi gördüm. Google puanınız şu an {lead.rating}. 4.5 puanın altındaki işletmeler yerel sıralamada ciddi müşteri kaybediyor.",
                    "solution": "Otomatik NFC/QR memnuniyet sistemiyle mutlu müşterilerinizden organik 5 yıldızlı yorum toplayıp puanınızı hızla yükseltebiliriz.",
                    "cta": "Bu hafta bölgenizde puanı yükselen 2 referans işletmemizi incelemek ister misiniz?"
                },
                "FEW_REVIEWS": {
                    "hook": f"{biz_name} harita kaydınızda yalnızca {lead.review_count} yorum bulunuyor. Bölgenizdeki rakiplerinizin yorum sayısı daha fazla olduğu için ilk 3 sıralamayı onlar alıyor.",
                    "solution": "Harita SEO ve yerel itibar çalışmasıyla işletmenizi haritada ilk 3'e taşımak.",
                    "cta": "Bölgenizdeki harita sıralama analizinizi 5 dakikada paylaşabilir miyim?"
                },
                "NO_SOCIAL_MEDIA": {
                    "hook": f"{biz_name} için dijital araştırmamızda aktif bir Instagram veya sosyal medya vitrini göremedik. Sektörünüzde müşterilerin %65'i siparişten önce sosyal medyaya bakıyor.",
                    "solution": "İşletmenizin marka değerini artıran profesyonel sosyal medya içerik ve reklam yönetimi.",
                    "cta": "Sektörünüze özel hazırladığımız örnek 1 haftalık içerik planını göndereyim mi?"
                },
                "NO_WHATSAPP_CONVERSION": {
                    "hook": f"{biz_name} profilinizi ziyaret eden potansiyel müşterilerin sizinle hızlıca mesajlaşabileceği doğrudan bir WhatsApp butonu bulunmuyor.",
                    "solution": "Tek tıkla randevu/fiyat sorulabilen akıllı WhatsApp karşılama sistemi.",
                    "cta": "Sistemin nasıl çalıştığını gösteren 1 dakikalık videoyu ileteyim mi?"
                }
            }

            default_hook_tr = {
                "hook": f"{city} bölgesindeki {biz_name} işletmenizin dijital görünürlüğünü ve Google Haritalar performansını analiz ettik.",
                "solution": "Bölgenizdeki yerel aramalardan gelen müşteri sayısını 2 katına çıkaracak yerel büyüme stratejisi.",
                "cta": "Detaylı büyüme analizini kısa bir PDF olarak paylaşmamı ister misiniz?"
            }

            hook_data = gap_hooks_tr.get(lead.primary_gap, default_hook_tr)

            if lang == "tr":
                if tone_lower in ("friendly", "samimi"):
                    if channel == "whatsapp":
                        subject = f"{biz_name} için İş Birliği & Çözüm Fikri"
                        message = (
                            f"Selamlar {biz_name} ekibi! 👋\n\n"
                            f"Ben {sender}, {agency}'ndan yazıyorum. {city} bölgesinde {category} profilinize rastladım ve işlerinizi çok beğendim.\n\n"
                            f"Küçük ama çok etkili bir çözüm fark ettik: {hook_data['hook']}\n\n"
                            f"Bunu sizin için çok kolay çözebiliriz: {hook_data['solution']}\n\n"
                            f"{hook_data['cta']}\n\n"
                            f"Görüşmek dileğiyle, sevgiler!"
                        )
                    else:
                        subject = f"Merhaba {biz_name} Ekibi — {city} Bölgesinde Hızlı Bir İnceleme"
                        message = (
                            f"Merhaba {biz_name} Ekibi,\n\n"
                            f"Umarım haftanız harika geçiyordur! Ben {sender}, {agency}'ndan ulaşıyorum.\n\n"
                            f"{city} bölgesinde {category} araştırması yaparken başarılı profilinizi inceledim. Sizin için işletmenize değer katacak pratik bir fırsat gördük:\n\n"
                            f"💡 Tespitimiz: {hook_data['hook']}\n\n"
                            f"Çözüm önerimiz: {hook_data['solution']}\n\n"
                            f"{hook_data['cta']}\n\n"
                            f"Müsait olduğunuzda kısa bir dönüş yaparsanız detayları hemen paylaşmaktan mutluluk duyarım.\n\n"
                            f"Sevgiler,\n"
                            f"{sender}\n"
                            f"{agency}"
                        )
                elif tone_lower in ("urgency", "direct", "aciliyet"):
                    if channel == "whatsapp":
                        subject = f"ACİL: {biz_name} Yerel Müşteri Kaybı Uyarısı"
                        message = (
                            f"{biz_name} Yetkilisine Önemli Not ⚠️\n\n"
                            f"Ben {sender}, {agency}'ndan ulaşıyorum. {city} bölgesinde {category} aramalarında rakiplerinizin öne geçmesine sebep olan kritik bir kayıp noktası var:\n\n"
                            f"🚨 Kritik Açık: {hook_data['hook']}\n\n"
                            f"Hemen harekete geçilmezse bölgenizdeki potansiyel müşteri kaybı katlanarak sürecek.\n\n"
                            f"⚡ Hızlı Çözümümüz: {hook_data['solution']}\n\n"
                            f"{hook_data['cta']}\n\n"
                            f"{sender} | {agency}"
                        )
                    else:
                        subject = f"DİKKAT: {biz_name} İçin Kritik Müşteri Kaybı & Yerel Sıralama Analizi ({city})"
                        message = (
                            f"Sayın {biz_name} Yetkilisi,\n\n"
                            f"Ben {sender}, {agency} kurucusuyum. {city} bölgesindeki {category} pazarını analiz ederken işletmenizin doğrudan müşteri kaybettiği somut bir açık tespit ettik:\n\n"
                            f"⚠️ Kritik Teşhis: {hook_data['hook']}\n\n"
                            f"Bu açık yüzünden her ay onlarca yerel müşteri doğrudan rakip firmalara kaptırılıyor. Zaman kaybetmeden müdahale edilmesi kritik önem taşıyor.\n\n"
                            f"🎯 24 Saatte Çözüm: {hook_data['solution']}\n\n"
                            f"{hook_data['cta']}\n\n"
                            f"Cevabınızı bekliyorum.\n\n"
                            f"{sender}\n"
                            f"{agency}"
                        )
                else:  # corporate / consultative
                    if channel == "whatsapp":
                        message = (
                            f"Merhaba {biz_name} yetkilisi,\n\n"
                            f"Ben {sender}, {agency}'ndan ulaşıyorum. {city} bölgesinde {category} araması yaparken profilinizi inceledim.\n\n"
                            f"💡 Önemli bir fırsat fark ettim: {hook_data['hook']}\n\n"
                            f"🎯 Sunduğumuz çözüm: {hook_data['solution']}\n\n"
                            f"{hook_data['cta']}\n\n"
                            f"İyi çalışmalar dilerim!"
                        )
                        subject = f"{biz_name} için Dijital Büyüme Fırsatı"
                    else:  # email
                        subject = f"{biz_name} için Önemli İnceleme ({city} Yerel Sıralama & Dönüşüm)"
                        message = (
                            f"Sayın {biz_name} Yetkilisi,\n\n"
                            f"Ben {sender}, {agency} kurucusuyum.\n\n"
                            f"{city} bölgesinde {category} hizmetleri arayan potansiyel müşterilerin davranışlarını incelerken profilinize rastladık. "
                            f"Mevcut durumunuzu incelediğimizde dikkat çeken bir nokta oldu:\n\n"
                            f"📌 Tespit: {hook_data['hook']}\n\n"
                            f"Bu durum her ay bölgenizden gelebilecek onlarca yeni müşterinin rakiplere yönelmesine yol açıyor.\n\n"
                            f"Biz bu sorunu şu şekilde çözüyoruz: {hook_data['solution']}\n\n"
                            f"{hook_data['cta']}\n\n"
                            f"Müsait olduğunuzda bu e-postayı 'Evet' diyerek yanıtlamanız yeterlidir, hemen iletebilirim.\n\n"
                            f"Saygılarımla,\n"
                            f"{sender}\n"
                            f"{agency}"
                        )
            else:  # English
                if tone_lower in ("friendly", "samimi"):
                    if channel == "whatsapp":
                        message = (
                            f"Hey {biz_name} team! 👋\n\n"
                            f"This is {sender} from {agency}. I came across your place while searching for great {category} spots in {city}.\n\n"
                            f"💡 Quick helpful observation: {hook_data['hook']}\n\n"
                            f"🎯 We can get this sorted for you super fast: {hook_data['solution']}\n\n"
                            f"Would you be open to checking out a quick preview we put together?\n\n"
                            f"Cheers,\n{sender}"
                        )
                        subject = f"Friendly idea for {biz_name}"
                    else:
                        subject = f"Quick note for {biz_name} ({city})"
                        message = (
                            f"Hi {biz_name} Team,\n\n"
                            f"Hope your week is off to a great start! I'm {sender} from {agency}.\n\n"
                            f"While researching top {category} businesses in {city}, I noticed an opportunity that could immediately boost your bookings:\n\n"
                            f"💡 Observation: {hook_data['hook']}\n\n"
                            f"How we help: {hook_data['solution']}\n\n"
                            f"Would you like me to send over a 2-minute overview?\n\n"
                            f"Best regards,\n{sender}\n{agency}"
                        )
                elif tone_lower in ("urgency", "direct", "aciliyet"):
                    if channel == "whatsapp":
                        message = (
                            f"Urgent note for {biz_name} team ⚠️\n\n"
                            f"This is {sender} from {agency}. You are currently losing {city} {category} inquiries to local competitors due to one critical bottleneck:\n\n"
                            f"🚨 Issue: {hook_data['hook']}\n\n"
                            f"⚡ Immediate fix: {hook_data['solution']}\n\n"
                            f"Can I share the 2-minute fix before your competitors widen the lead?\n\n"
                            f"{sender} | {agency}"
                        )
                        subject = f"Urgent lead leak at {biz_name}"
                    else:
                        subject = f"Action Required: {biz_name} is losing local clients in {city}"
                        message = (
                            f"Attention: {biz_name} Leadership,\n\n"
                            f"This is {sender} from {agency}. While auditing {category} providers in {city}, we uncovered a critical conversion bottleneck:\n\n"
                            f"⚠️ Bottleneck: {hook_data['hook']}\n\n"
                            f"Every week this remains unaddressed, potential clients choose competing businesses in {city}.\n\n"
                            f"🎯 Turnaround Plan: {hook_data['solution']}\n\n"
                            f"Reply 'YES' to receive the implementation steps today.\n\n"
                            f"Regards,\n{sender}\n{agency}"
                        )
                else:  # corporate / consultative
                    if channel == "whatsapp":
                        message = (
                            f"Hi {biz_name} team,\n\n"
                            f"This is {sender} from {agency}. I noticed your business while analyzing top {category} places in {city}.\n\n"
                            f"💡 Quick observation: We noticed a key opportunity to increase your inbound leads ({hook_data['hook']}).\n\n"
                            f"🎯 We can solve this: {hook_data['solution']}\n\n"
                            f"Would you be open to seeing a quick 2-minute mockup we built for you?\n\n"
                            f"Best regards,\n{sender}"
                        )
                        subject = f"Growth opportunity for {biz_name}"
                    else:
                        subject = f"Quick question regarding {biz_name} ({city})"
                        message = (
                            f"Hi {biz_name} Team,\n\n"
                            f"I came across your profile while reviewing {category} providers in {city}.\n\n"
                            f"While your location and reputation look strong ({rating_str}), there is a clear bottleneck costing you new inquiries each week:\n\n"
                            f"🔍 Key Finding: {hook_data['hook']}\n\n"
                            f"Solution: {hook_data['solution']}\n\n"
                            f"Would you like me to send over a quick 2-minute overview video on how to implement this?\n\n"
                            f"Best,\n"
                            f"{sender}\n"
                            f"{agency}"
                        )

        # Generate direct WhatsApp click link if phone is available
        whatsapp_url = ""
        if lead.whatsapp:
            encoded_msg = urllib.parse.quote(message)
            if "wa.me/" in lead.whatsapp:
                phone_num = lead.whatsapp.split("wa.me/")[-1].split("?")[0]
                whatsapp_url = f"https://wa.me/{phone_num}?text={encoded_msg}"
            else:
                whatsapp_url = f"{lead.whatsapp}&text={encoded_msg}"

        # Apply ROI Calculation Hook if provided
        if roi_metrics and isinstance(roi_metrics, dict):
            deal_val = str(roi_metrics.get("deal_value") or "").strip()
            payback = str(roi_metrics.get("payback_days") or "").strip()
            roi_pct = str(roi_metrics.get("roi_percent") or "").strip()
            if deal_val:
                if lang == "tr":
                    pb_str = f"tahmini {payback} günde" if payback else "kısa sürede"
                    pct_str = f" ve %{roi_pct} net getiri" if roi_pct else ""
                    roi_text = f"\n\n📊 Finansal ROI Analizi: Ortalama {deal_val} tutarındaki bu yatırım, işletmenize sağlayacağı ciro ve verimlilik artışıyla {pb_str} kendini amorti eder{pct_str} sağlar."
                else:
                    pb_str = f"in an estimated {payback} days" if payback else "rapidly"
                    pct_str = f" with an estimated {roi_pct}% ROI" if roi_pct else ""
                    roi_text = f"\n\n📊 Financial ROI Analysis: An average investment of {deal_val} pays for itself {pb_str}{pct_str} through increased revenue and efficiency."
                message = message.strip() + roi_text
                # Recompute whatsapp_url with updated message
                if lead.whatsapp:
                    encoded_msg = urllib.parse.quote(message)
                    if "wa.me/" in lead.whatsapp:
                        phone_num = lead.whatsapp.split("wa.me/")[-1].split("?")[0]
                        whatsapp_url = f"https://wa.me/{phone_num}?text={encoded_msg}"
                    else:
                        whatsapp_url = f"{lead.whatsapp}&text={encoded_msg}"

        return {
            "provider": "offline-pro-templates",
            "channel": channel,
            "tone": tone,
            "language": lang,
            "subject": subject,
            "content": message,
            "whatsapp_direct_url": whatsapp_url,
            "primary_gap": lead.primary_gap,
            "product_pitch_type": p_type,
            "product_name": product_name,
            "sequence_step": sequence_step,
            "roi_metrics": roi_metrics
        }

    def _build_product_pitch_content(
        self,
        lead: Lead,
        p_type: str,
        product_name: str,
        channel: str,
        tone_lower: str,
        lang: str,
        sender: str,
        agency: str
    ) -> tuple:
        biz_name = lead.name or "İşletme Yetkilisi"
        city = lead.city or "bölgenizdeki"
        category = lead.category or "sektör"

        if lang == "tr":
            if p_type == "hair_dye":
                if tone_lower in ("friendly", "samimi"):
                    if channel == "whatsapp":
                        subject = f"{biz_name} için Profesyonel Saç Boyası & Salon Tedariği"
                        message = (
                            f"Selamlar {biz_name} ekibi! 👋\n\n"
                            f"Ben {sender}, {agency}'ndan ulaşıyorum. {city} bölgesindeki salonunuzu inceledim ve tarzınızı çok beğendim.\n\n"
                            f"Kuaför ve güzellik salonlarına doğrudan profesyonel toptan saç boyası, oksidan ve salon sarf malzemeleri tedariği sağlıyoruz. Salonlara özel avantajlı toptan fiyat listemiz ve ilk sipariş öncesi salonunuzda test edebilmeniz için ücretsiz numune / deneme setimiz bulunuyor. 🎨📦\n\n"
                            f"Salon toptan fiyat listemizi ve renk kartelamızı WhatsApp'tan iletmemi ister misiniz?\n\n"
                            f"Görüşmek dileğiyle, bol kazançlar!"
                        )
                    else:
                        subject = f"{biz_name} İçin Profesyonel Saç Boyası & Salon Tedariği Toptan Fiyat Listesi ({city})"
                        message = (
                            f"Merhaba {biz_name} Ekibi,\n\n"
                            f"Umarım haftanız harika geçiyordur! Ben {sender}, {agency}'ndan ulaşıyorum.\n\n"
                            f"{city} bölgesinde kuaför ve güzellik salonları için profesyonel saç boyaları, bakım ürünleri ve sarf malzemeleri tedarik ediyoruz.\n\n"
                            f"Kuaförlerimize sunduğumuz ayrıcalıklar:\n"
                            f"• Doğrudan toptan fiyat avantajı ve salon kar marjını artıran özel kuaför iskontoları\n"
                            f"• Zengin renk kartelası, %100 beyaz kapatma ve amonyaksız vegan seriler\n"
                            f"• Aynı gün kargo ve hızlı sevkiyat garantisi\n"
                            f"• Salonunuzda bizzat denemeniz için Ücretsiz Numune / Tester Deneme Kiti\n\n"
                            f"Müsait olduğunuzda güncel toptan fiyat listemizi ve renk kartelamızı paylaşmaktan memnuniyet duyarım.\n\n"
                            f"Saygılarımla,\n{sender}\n{agency}"
                        )
                elif tone_lower in ("urgency", "direct", "aciliyet"):
                    if channel == "whatsapp":
                        subject = f"ACİL: {biz_name} Salon Maliyet Avantajı & Toptan Saç Boyası"
                        message = (
                            f"{biz_name} Salon Yetkilisine Önemli Not ⚠️\n\n"
                            f"Ben {sender}, {agency}'ndan ulaşıyorum. {city} bölgesinde salonların artan saç boyası ve kozmetik tedarik maliyetlerini doğrudan toptan fabrika fiyatlarıyla %25-35 oranında düşürüyoruz.\n\n"
                            f"Yüksek pigmentli, kalıcı profesyonel saç boyası serimizi salonunuzda test etmeniz için ücretsiz numune kiti gönderiyoruz. Aynı gün kargo ve hızlı sevkiyat sağlıyoruz.\n\n"
                            f"Bugün deneme kitinizi ve kuaför özel toptan iskonto listesini gönderebilir miyim?\n\n"
                            f"{sender} | {agency}"
                        )
                    else:
                        subject = f"DİKKAT: {biz_name} Salon Maliyet Avantajı & Toptan Saç Boyası Tedariği"
                        message = (
                            f"Sayın {biz_name} Yetkilisi,\n\n"
                            f"Ben {sender}, {agency} kurucusuyum. {city} bölgesindeki kuaför salonlarının en büyük gider kalemi olan saç boyası ve salon sarf malzemelerinde aracısız toptan tedarik modeli sunuyoruz.\n\n"
                            f"🎯 Salonunuza Kazandırdıklarımız:\n"
                            f"1. Doğrudan toptan fiyatlandırma ile anında %30'a varan maliyet tasarrufu\n"
                            f"2. Ücretsiz tester/numune setiyle sıfır riskli deneme imkanı\n"
                            f"3. Sürekli stok garantisi ve aynı gün teslimat\n\n"
                            f"Bu e-postayı 'Evet' olarak yanıtlamanız durumunda numune setinizi ve fiyat kataloğumuzu hemen kargolayabiliriz.\n\n"
                            f"Saygılarımla,\n{sender}\n{agency}"
                        )
                else:  # consultative
                    if channel == "whatsapp":
                        subject = f"{biz_name} için Profesyonel Saç Boyası Tedarik Ortaklığı"
                        message = (
                            f"Merhaba {biz_name} yetkilisi,\n\n"
                            f"Ben {sender}, {agency}'ndan ulaşıyorum. {city} bölgesindeki kuaför salonunuzu inceledim.\n\n"
                            f"Kuaförlerimize özel profesyonel saç boyası, bakım ürünleri ve salon sarf malzemeleri tedariği sağlıyoruz. Yüksek renk kalitesi, zengin kartela ve kuaför salonlarına özel toptan fiyat avantajı sunuyoruz.\n\n"
                            f"Ayrıca ilk etapta kalitemizi bizzat salonunuzda denemeniz için ücretsiz numune deneme kiti temin ediyoruz.\n\n"
                            f"Güncel salon toptan kataloğumuzu ve numune detaylarını WhatsApp'tan paylaşmamı ister misiniz?\n\n"
                            f"İyi çalışmalar dilerim!"
                        )
                    else:
                        subject = f"{biz_name} İçin Profesyonel Saç Boyası & Salon Tedarik Ortaklığı"
                        message = (
                            f"Sayın {biz_name} Yetkilisi,\n\n"
                            f"Ben {sender}, {agency}'ndan ulaşıyorum.\n\n"
                            f"{city} bölgesinde kuaförlük sektöründeki başarılı çalışmalarınızı memnuniyetle takip ediyoruz. Salonunuzun hizmet kalitesini ve karlılığını artıracak profesyonel saç boyası ve salon tedarik çözümlerimizle yanınızdayız.\n\n"
                            f"📌 Çözüm ve Avantajlarımız:\n"
                            f"• Kuaför salonlarına özel toptan fiyat avantajı ve esnek koli bazlı sipariş imkanı\n"
                            f"• Üstün beyaz kapatma gücü ve yoğun pigmentli geniş renk serileri\n"
                            f"• Ön deneme için adrese teslim Ücretsiz Numune / Tester Paketi\n"
                            f"• Hızlı tedarik zinciri ve kesintisiz stok desteği\n\n"
                            f"Uygun olduğunuzda toptan fiyat listemizi ve ürün kartelamızı incelemeniz için iletebiliriz.\n\n"
                            f"Saygılarımla,\n{sender}\n{agency}"
                        )

            elif p_type == "steam_iron":
                if tone_lower in ("friendly", "samimi"):
                    if channel == "whatsapp":
                        subject = f"{biz_name} için Buharlı Ütü & Tesisat Çözümleri"
                        message = (
                            f"Selamlar {biz_name} atölye ekibi! 👋\n\n"
                            f"Ben {sender}, {agency}'ndan yazıyorum. {city} bölgesindeki tekstil/dikim işletmenizi inceledim.\n\n"
                            f"Tekstil atölyeleri, konfeksiyon ve terziler için Silter tipi sanayi tipi buharlı ütü makineleri, merkezi buhar kazanı tesisat kurulumu ve yedek parça desteği sunuyoruz. Ütüleme hızınızı ve buhar veriminizi en üst seviyeye çıkarıyoruz. 👔⚡\n\n"
                            f"Atölyenize uygun tesisat ve ütü makinesi çözümlerimizi, güncel kampanya fiyat listemizi WhatsApp'tan göndereyim mi?\n\n"
                            f"Bereketli işler dilerim!"
                        )
                    else:
                        subject = f"{biz_name} İçin Sanayi Tipi Buharlı Ütü & Tesisat Kurulum Çözümleri ({city})"
                        message = (
                            f"Merhaba {biz_name} Ekibi,\n\n"
                            f"Umarım işleriniz yolundadır. Ben {sender}, {agency}'ndan ulaşıyorum.\n\n"
                            f"{city} bölgesinde tekstil atölyeleri, terziler ve konfeksiyon imalatçıları için Silter sanayi tipi buharlı ütü sistemleri ve merkezi buhar tesisatı kurulumu gerçekleştiriyoruz.\n\n"
                            f"Atölyenize sağladığımız çözümler:\n"
                            f"• Silter sanayi tipi buharlı ütüler, paskaralar ve buhar kazanları\n"
                            f"• Atölye içi anahtar teslim buhar tesisatı montajı ve borulama\n"
                            f"• Orijinal yedek parça (rezistans, ventiller, teflon pabuçlar) ve yerinde teknik servis\n"
                            f"• Enerji tasarruflu, yüksek buhar basınçlı kesintisiz çalışma imkanı\n\n"
                            f"Atölyenizin kapasitesine uygun makine ve tesisat teklifimizi paylaşmamı ister misiniz?\n\n"
                            f"Saygılarımla,\n{sender}\n{agency}"
                        )
                elif tone_lower in ("urgency", "direct", "aciliyet"):
                    if channel == "whatsapp":
                        subject = f"ACİL: {biz_name} Atölye Buhar & Ütü Tesisatı"
                        message = (
                            f"{biz_name} Atölye Yetkilisine Acil Not ⚠️\n\n"
                            f"Ben {sender}, {agency}'ndan ulaşıyorum. Ütü arızaları ve yetersiz buhar basıncı tekstil atölyelerinde teslimat gecikmelerine ve ciddi iş kaybına yol açar.\n\n"
                            f"Silter tipi sanayi tipi buharlı ütü makineleri, yüksek basınçlı buhar kazanları ve sıfır arıza garantili tesisat kurulumu sağlıyoruz. 24 saatte hızlı montaj, yerinde teknik servis ve orijinal yedek parça güvencesi sunuyoruz.\n\n"
                            f"Atölyenizin ihtiyacına özel ütü & tesisat teklifini hemen iletebilir miyim?\n\n"
                            f"{sender} | {agency}"
                        )
                    else:
                        subject = f"DİKKAT: {biz_name} Atölye Ütü & Buhar Tesisatı Verimlilik Raporu"
                        message = (
                            f"Sayın {biz_name} Yetkilisi,\n\n"
                            f"Ben {sender}, {agency} teknik koordinatörüyüm. {city} bölgesinde tekstil imalatında yaşanan ütü aksamaları üretim bandını doğrudan yavaşlatmaktadır.\n\n"
                            f"⚡ Atölyeniz İçin Hızlı Çözümümüz:\n"
                            f"• Yüksek kapasiteli Silter tipi sanayi buharlı ütü sistemleri ve paskaralar\n"
                            f"• Profesyonel merkezi buhar tesisatı kurulumu ve hat montajı\n"
                            f"• Anında orijinal yedek parça temini ve periyodik bakım garantisi\n\n"
                            f"Atölyenizde ütüleme hızını artıran tesisat teklifimizi incelemek için 'Evet' yanıtını iletmeniz yeterlidir.\n\n"
                            f"Saygılarımla,\n{sender}\n{agency}"
                        )
                else:  # consultative
                    if channel == "whatsapp":
                        subject = f"{biz_name} için Sanayi Tipi Buharlı Ütü & Tesisat Kurulumu"
                        message = (
                            f"Merhaba {biz_name} yetkilisi,\n\n"
                            f"Ben {sender}, {agency}'ndan ulaşıyorum. {city} bölgesindeki atölyenizi/işletmenizi inceledim.\n\n"
                            f"Tekstil atölyeleri, konfeksiyon ve terziler için Silter tipi sanayi tipi buharlı ütü sistemleri, merkezi buhar kazanı tesisatı montajı, periyodik bakım ve orijinal yedek parça hizmeti veriyoruz.\n\n"
                            f"İş gücünden tasarruf sağlayan, kumaş parlamasını önleyen ve ütüleme verimini artıran çözümlerimiz mevcuttur.\n\n"
                            f"Atölyenize uygun tesisat ve buharlı ütü makinesi fiyat kataloğumuzu WhatsApp üzerinden iletmemi ister misiniz?\n\n"
                            f"İyi çalışmalar dilerim!"
                        )
                    else:
                        subject = f"{biz_name} İçin Sanayi Tipi Buharlı Ütü Sistemleri & Tesisat Kurulumu"
                        message = (
                            f"Sayın {biz_name} Yetkilisi,\n\n"
                            f"Ben {sender}, {agency}'ndan ulaşıyorum.\n\n"
                            f"{city} bölgesinde tekstil ve konfeksiyon sektöründe faaliyet gösteren işletmenizin üretim kalitesini artıracak sanayi tipi buharlı ütü ve buhar tesisatı çözümlerimizi sunmak isteriz.\n\n"
                            f"🔧 Hizmet Kapsamımız:\n"
                            f"• Silter tipi sanayi buharlı ütüler, vakumlu paskaralar ve otomatik su beslemeli buhar kazanları\n"
                            f"• Atölye içi komple buhar tesisatı projelendirme ve profesyonel montaj\n"
                            f"• Orijinal yedek parça, teflon altlıklar ve periyodik teknik bakım desteği\n"
                            f"• Minimum enerji tüketimiyle maksimum buhar debisi ve kusursuz ütüleme kalitesi\n\n"
                            f"Atölyenize özel hazırlayabileceğimiz avantajlı makine & tesisat teklifimizi incelemeniz için iletebiliriz.\n\n"
                            f"Saygılarımla,\n{sender}\n{agency}"
                        )

            elif p_type == "software":
                if tone_lower in ("friendly", "samimi"):
                    if channel == "whatsapp":
                        subject = f"{biz_name} için Özel Web & Yazılım Çözümü"
                        message = (
                            f"Selamlar {biz_name} ekibi! 👋\n\n"
                            f"Ben {sender}, {agency}'ndan ulaşıyorum. {city} bölgesinde {category} profilinize rastladım ve işlerinizi çok beğendim.\n\n"
                            f"İşletmelere özel web sitesi, mobil randevu/sipariş yazılımları ve müşteri yönetim (CRM) otomasyonları geliştiriyoruz. Manuel iş yükünü sıfırlayıp dijitalden gelen müşteri sayısını katlıyoruz. 💻🚀\n\n"
                            f"İşletmeniz için hazırladığımız 1 dakikalık canlı yazılım demosunu WhatsApp'tan iletmemi ister misiniz?\n\n"
                            f"Görüşmek dileğiyle!"
                        )
                    else:
                        subject = f"{biz_name} İçin Özel Yazılım & Dijital Müşteri Kazanım Çözümü ({city})"
                        message = (
                            f"Merhaba {biz_name} Ekibi,\n\n"
                            f"Umarım haftanız harika geçiyordur! Ben {sender}, {agency}'ndan ulaşıyorum.\n\n"
                            f"{city} bölgesinde {category} sektöründeki çalışmalarınızı inceledik. İşletmenizin dijital süreçlerini hızlandıracak ve yeni müşteri akışını otomatikleştirecek yazılım altyapıları sunuyoruz.\n\n"
                            f"🚀 Sunduğumuz Yazılım Çözümleri:\n"
                            f"• Hızlı, mobil uyumlu ve modern web sitesi / web uygulaması\n"
                            f"• 7/24 randevu alma, sipariş ve müşteri takip (CRM) yazılımı\n"
                            f"• Google Haritalar ve yerel aramalardan gelen müşterileri yakalayan akıllı otomasyon\n\n"
                            f"Canlı demo sistemimizi ve size özel çözüm dosyamızı paylaşmamı ister misiniz?\n\n"
                            f"Saygılarımla,\n{sender}\n{agency}"
                        )
                elif tone_lower in ("urgency", "direct", "aciliyet"):
                    if channel == "whatsapp":
                        subject = f"ACİL: {biz_name} Dijital Yazılım & Müşteri Kaybı Uyarısı"
                        message = (
                            f"{biz_name} Yetkilisine Önemli Not ⚠️\n\n"
                            f"Ben {sender}, {agency}'ndan ulaşıyorum. {city} bölgesinde rakipleriniz modern web ve otomasyon yazılımlarıyla dijital müşterileri toplarken işletmeniz müşteri kaybediyor.\n\n"
                            f"48 saatte kurulan modern web yazılımı, WhatsApp randevu otomasyonu ve CRM entegrasyonuyla müşteri kaybını anında durduruyoruz.\n\n"
                            f"Sizin için hazırladığımız hızlı dönüşüm taslağını WhatsApp'tan incelemeniz için gönderebilir miyim?\n\n"
                            f"{sender} | {agency}"
                        )
                    else:
                        subject = f"DİKKAT: {biz_name} İçin Dijital Yazılım & Müşteri Kaybı Analizi"
                        message = (
                            f"Sayın {biz_name} Yetkilisi,\n\n"
                            f"Ben {sender}, {agency} kurucusuyum. {city} pazarında {category} araması yapan potansiyel müşterilerin büyük bölümü randevu ve iletişimini dijital yazılımlar üzerinden tamamlamaktadır.\n\n"
                            f"Mevcut altyapınızın yetersizliği nedeniyle her hafta onlarca müşteri rakip firmalara geçmektedir.\n\n"
                            f"🎯 48 Saatte Kurulan Yazılım Paketimiz:\n"
                            f"• Mobil uyumlu akıllı web portalı\n"
                            f"• Otomatik müşteri rezervasyon ve bildirim sistemi\n"
                            f"• Yerel Google SEO ve dönüşüm hunisi\n\n"
                            f"Bu e-postayı 'Evet' diyerek yanıtlayın, sistemi bugün işletmenize kuralım.\n\n"
                            f"Saygılarımla,\n{sender}\n{agency}"
                        )
                else:  # consultative
                    if channel == "whatsapp":
                        subject = f"{biz_name} için Özel Web & Yazılım Otomasyonu"
                        message = (
                            f"Merhaba {biz_name} yetkilisi,\n\n"
                            f"Ben {sender}, {agency}'ndan ulaşıyorum. {city} bölgesindeki işletmenizi ve dijital varlığınızı inceledim.\n\n"
                            f"İşletmenize özel web yazılımı, online randevu/sipariş sistemleri ve dijital müşteri edinme otomasyonları geliştiriyoruz.\n\n"
                            f"İşletmenizin yerel müşteri dönüşümünü 2 katına çıkaracak yazılım çözümümüzü ve canlı örneklerimizi WhatsApp'tan paylaşmamı ister misiniz?\n\n"
                            f"İyi çalışmalar dilerim!"
                        )
                    else:
                        subject = f"{biz_name} İçin Kurumsal Web & Yazılım Otomasyonu Teklifi"
                        message = (
                            f"Sayın {biz_name} Yetkilisi,\n\n"
                            f"Ben {sender}, {agency}'ndan ulaşıyorum.\n\n"
                            f"{city} bölgesinde {category} hizmetleri sunan işletmenizin dijitalleşme süreçlerini hızlandırmak ve operasyonel verimliliğinizi artırmak adına özel yazılım çözümleri geliştiriyoruz.\n\n"
                            f"💡 Yazılım ve Otomasyon Kapsamımız:\n"
                            f"• Mobil öncelikli kurumsal web arayüzleri ve müşteri portalları\n"
                            f"• Online randevu, fiyat teklifi ve sipariş yönetim otomasyonları\n"
                            f"• WhatsApp & SMS entegrasyonlu akıllı müşteri takip sistemleri (CRM)\n"
                            f"• Google arama sonuçlarında üst sıralara taşıyan teknik altyapı\n\n"
                            f"Müsait olduğunuzda işletmenize özel hazırladığımız sunum dosyasını ve demomuzu iletmek isteriz.\n\n"
                            f"Saygılarımla,\n{sender}\n{agency}"
                        )

            else:  # custom product
                prod = product_name.strip() if product_name else "Özel Ürün/Hizmet"
                if channel == "whatsapp":
                    subject = f"{biz_name} için {prod} Kurumsal Teklif"
                    message = (
                        f"Merhaba {biz_name} yetkilisi,\n\n"
                        f"Ben {sender}, {agency}'ndan ulaşıyorum. {city} bölgesindeki faaliyetlerinizi inceledim.\n\n"
                        f"İşletmeniz için yüksek kalite, avantajlı fiyat ve güvenilir teslimat garantisiyle '{prod}' çözümleri sunuyoruz.\n\n"
                        f"{biz_name} için hazırladığımız özel kurumsal fiyat teklifimizi ve detaylı kataloğumuzu WhatsApp üzerinden paylaşmamı ister misiniz?\n\n"
                        f"İyi çalışmalar dilerim!"
                    )
                else:
                    subject = f"{biz_name} İçin {prod} Kurumsal Teklif & İş Birliği Fırsatı ({city})"
                    message = (
                        f"Sayın {biz_name} Yetkilisi,\n\n"
                        f"Ben {sender}, {agency}'ndan ulaşıyorum.\n\n"
                        f"{city} bölgesindeki başarılı ticari faaliyetlerinizi memnuniyetle takip ediyoruz. İşletmenizin ihtiyaçlarına tam uyum sağlayan kurumsal '{prod}' çözümlerimizle hizmetinizdeyiz.\n\n"
                        f"📦 Sunduğumuz Kurumsal Avantajlar:\n"
                        f"• Doğrudan üretici/toptan fiyatlandırma ve esnek ödeme koşulları\n"
                        f"• Yüksek kalite standartları ve kesintisiz tedarik garantisi\n"
                        f"• Hızlı teslimat ve satış sonrası tam kurumsal destek\n\n"
                        f"{biz_name} için hazırladığımız özel teklif dosyasını ve ürün kataloğumuzu incelemek isterseniz bu e-postayı yanıtlamanız yeterlidir.\n\n"
                        f"Saygılarımla,\n{sender}\n{agency}"
                    )

        else:  # English
            if p_type == "hair_dye":
                if channel == "whatsapp":
                    subject = f"Wholesale Professional Hair Dye & Salon Supplies for {biz_name}"
                    message = (
                        f"Hi {biz_name} team! 👋\n\n"
                        f"This is {sender} from {agency}. We supply salons in {city} with wholesale premium professional hair dye, hair care products, and salon essentials. We offer exclusive salon tier pricing and a free sample trial kit for your stylists to test out.\n\n"
                        f"Would you like me to send over our wholesale catalog and shade chart via WhatsApp?\n\n"
                        f"Best regards,\n{sender}"
                    )
                else:
                    subject = f"Wholesale Hair Dye & Salon Supplies for {biz_name} ({city})"
                    message = (
                        f"Hi {biz_name} Team,\n\n"
                        f"This is {sender} from {agency}. We partner with premier hair salons across {city} to provide high-performance professional hair dye, hair color, and supplies at direct wholesale rates.\n\n"
                        f"What we offer your salon:\n"
                        f"• Direct wholesale pricing with high margin markups\n"
                        f"• Rich shade palette with 100% grey coverage\n"
                        f"• Fast dispatch and continuous stock reliability\n"
                        f"• Complimentary tester & sample kit for your styling team\n\n"
                        f"Would you be open to receiving our wholesale catalog and sample kit?\n\n"
                        f"Best regards,\n{sender}\n{agency}"
                    )
            elif p_type == "steam_iron":
                if channel == "whatsapp":
                    subject = f"Industrial Steam Iron & Boiler Installation for {biz_name}"
                    message = (
                        f"Hello {biz_name} team! 👋\n\n"
                        f"This is {sender} from {agency}. We provide textile workshops and tailors in {city} with industrial steam iron systems (Silter type), central boiler setup, pipeline installation, and genuine spare parts.\n\n"
                        f"Would you like me to share our machinery catalog and workshop installation packages on WhatsApp?\n\n"
                        f"Best regards,\n{sender}"
                    )
                else:
                    subject = f"Industrial Steam Irons & Workshop Installation for {biz_name} ({city})"
                    message = (
                        f"Attention: {biz_name} Management,\n\n"
                        f"This is {sender} from {agency}. We specialize in turnkey industrial steam ironing setups and central steam boiler installations for textile manufacturers and tailors in {city}.\n\n"
                        f"Our solutions include:\n"
                        f"• Heavy-duty industrial steam irons (Silter style) and vacuum ironing tables\n"
                        f"• High-pressure boiler pipeline design and workshop assembly\n"
                        f"• On-site maintenance and genuine spare parts replacement\n"
                        f"• Significant energy efficiency and zero downtime guarantee\n\n"
                        f"Reply to this email to receive our equipment catalog and quote.\n\n"
                        f"Best regards,\n{sender}\n{agency}"
                    )
            elif p_type == "software":
                if channel == "whatsapp":
                    subject = f"Custom Software & Automation for {biz_name}"
                    message = (
                        f"Hi {biz_name} team! 👋\n\n"
                        f"This is {sender} from {agency}. We build custom software, web apps, client booking/order systems, and workflow automations tailored for businesses in {city}.\n\n"
                        f"Would you be open to checking out a quick 1-minute live demo we built for your sector?\n\n"
                        f"Best regards,\n{sender}"
                    )
                else:
                    subject = f"Custom Software & Client Acquisition for {biz_name} ({city})"
                    message = (
                        f"Hi {biz_name} Team,\n\n"
                        f"This is {sender} from {agency}. We develop custom software, web platforms, automated booking systems, and mini-CRMs designed to streamline operations and double inbound leads for businesses in {city}.\n\n"
                        f"Key capabilities:\n"
                        f"• Fast, mobile-responsive custom web applications\n"
                        f"• 24/7 automated booking and customer communication funnels\n"
                        f"• Local Google Maps search optimization and digital presence\n\n"
                        f"Would you like me to send over our solution overview and demo preview?\n\n"
                        f"Best,\n{sender}\n{agency}"
                    )
            else:
                prod = product_name.strip() if product_name else "Specialized B2B Offering"
                if channel == "whatsapp":
                    subject = f"Corporate {prod} Proposal for {biz_name}"
                    message = (
                        f"Hi {biz_name} team,\n\n"
                        f"This is {sender} from {agency}. We provide premium '{prod}' solutions with dependable delivery and direct corporate pricing for businesses in {city}.\n\n"
                        f"Would you like me to send over our product catalog and pricing preview on WhatsApp?\n\n"
                        f"Best regards,\n{sender}"
                    )
                else:
                    subject = f"Partnership & Corporate {prod} Proposal for {biz_name}"
                    message = (
                        f"Dear {biz_name} Leadership,\n\n"
                        f"This is {sender} from {agency}. We deliver high-grade corporate '{prod}' solutions designed to maximize efficiency and value for companies in {city}.\n\n"
                        f"Key Benefits:\n"
                        f"• Direct manufacturer/wholesale pricing\n"
                        f"• Guaranteed availability and prompt dispatch\n"
                        f"• Dedicated account support and trial packages\n\n"
                        f"Reply to this email if you would like to receive our complete specification catalog.\n\n"
                        f"Best regards,\n{sender}\n{agency}"
                    )

        return subject, message

    def _build_sequence_pitch(
        self,
        lead: Lead,
        p_type: str,
        product_name: str,
        channel: str,
        tone_lower: str,
        lang: str,
        sender: str,
        agency: str,
        step: int
    ) -> tuple:
        biz_name = lead.name or "İşletme Yetkilisi"
        city = lead.city or "bölgenizdeki"
        prod = product_name.strip() if product_name else "çözümümüz"

        if lang == "tr":
            if step == 2:
                # Step 2: Follow-up (Social proof, case study, value drop)
                if p_type == "hair_dye":
                    if channel == "whatsapp":
                        subject = f"Re: {biz_name} için kuaför salonu toptan boya tedariği"
                        message = (
                            f"Selamlar {biz_name} ekibi! 👋\n\n"
                            f"Ben {sender}, {agency}'ndan. Birkaç gün önce ilettiğim toptan kuaför saç boyası ve salon sarf malzemeleriyle ilgili kısa bir referans ve vaka çalışması paylaşmak istedim.\n\n"
                            f"📊 Örnek Sonuç: Benzer ölçekteki bir kuaför salonumuz doğrudan toptan tedarik modelimize geçtikten sonra aylık boya ve sarf malzeme maliyetini %32 düşürürken, renk pigmenti ve beyaz kapatma kalitesinden ödün vermedi.\n\n"
                            f"🎨 Salonunuzda ücretsiz test edebilmeniz için hazırladığımız tester / numune kitini gönderebileceğimiz adresi iletmeniz yeterli olur mu?\n\n"
                            f"Kolaylıklar ve bol kazançlar dilerim!"
                        )
                    else:
                        subject = f"Takip: {biz_name} İçin Salon Maliyet Tasarrufu & Örnek Vaka Analizi ({city})"
                        message = (
                            f"Merhaba {biz_name} Ekibi,\n\n"
                            f"Ben {sender}, {agency}'ndan. Geçtiğimiz günlerde salonunuz için toptan profesyonel saç boyası ve sarf malzemesi tedariği konusunda kısa bir not paylaşmıştım.\n\n"
                            f"Kuaförlerimizin en çok memnun kaldığı somut kazanımlar:\n"
                            f"• Ortalama %30 maliyet tasarrufu sağlayan doğrudan salon toptan iskontoları\n"
                            f"• Yoğun salon temposunda aynı gün kargoyla sıfır stok riski\n"
                            f"• %100 beyaz kapatan, amonyaksız zengin renk serileri\n\n"
                            f"Salonunuzda bizzat deneyebilmeniz için Ücretsiz Numune / Tester Paketimizi kargolamaktan memnuniyet duyarız.\n\n"
                            f"Bu e-postayı salon teslimat adresinizle yanıtlamanız yeterlidir.\n\n"
                            f"Saygılarımla,\n{sender}\n{agency}"
                        )
                elif p_type == "steam_iron":
                    if channel == "whatsapp":
                        subject = f"Re: {biz_name} için sanayi tipi ütü ve buhar sistemleri"
                        message = (
                            f"Selamlar {biz_name} yetkilisi! 👋\n\n"
                            f"Ben {sender}, {agency}'ndan. Atölyeniz için ilettiğim Silter tipi sanayi buharlı ütü sistemleri ve merkezi tesisat desteği hakkında kısa bir referans aktarmak istedim.\n\n"
                            f"⚙️ Örnek Vaka: Benzer bir tekstil atölyesinde kurduğumuz merkezi buhar hattı ve yüksek basınçlı ütü sistemi sayesinde günlük ütüleme hızı %40 arttı ve kireç kaynaklı makine duruşları tamamen önlendi.\n\n"
                            f"Atölyenizdeki mevcut ütü ve kazan durumuna göre hazırladığımız keşif & tasarruf tablosunu WhatsApp'tan paylaşmamı ister misiniz?\n\n"
                            f"İyi çalışmalar dilerim!"
                        )
                    else:
                        subject = f"Takip: {biz_name} İçin Sanayi Tipi Ütü Verimliliği & Vaka Özeti ({city})"
                        message = (
                            f"Sayın {biz_name} Yetkilisi,\n\n"
                            f"Ben {sender}, {agency}'ndan. Atölyenizdeki ütüleme performansı, merkezi buhar tesisatı ve Silter sanayi tipi sistemlerle ilgili ilettiğim teklifimize istinaden yazıyorum.\n\n"
                            f"Atölyelere Sağladığımız Somut Katma Değer:\n"
                            f"• Yüksek basınçlı kuru buhar ile %40 daha hızlı ütüleme ve sıfır leke garantisi\n"
                            f"• Enerji tasarruflu rezistans teknolojisiyle elektrik faturalarında %25 düşüş\n"
                            f"• Orijinal Silter yedek parça ve yerinde hızlı teknik servis desteği\n\n"
                            f"Atölyeniz için en uygun kapasiteyi ve amortisman tablosunu incelemek isterseniz kısa bir yanıt vermeniz yeterlidir.\n\n"
                            f"Saygılarımla,\n{sender}\n{agency}"
                        )
                elif p_type == "software":
                    if channel == "whatsapp":
                        subject = f"Re: {biz_name} için yazılım & müşteri otomasyonu"
                        message = (
                            f"Selamlar {biz_name} ekibi! 👋\n\n"
                            f"Ben {sender}, {agency}'ndan. Birkaç gün önce {city} bölgesindeki işletmeniz için önerdiğim akıllı randevu ve müşteri kazanım sistemi hakkında hızlı bir referans paylaşmak istedim.\n\n"
                            f"📈 Gerçek Sonuç: Benzer bir yerel işletmede kurduğumuz tek tıkla WhatsApp ve harita entegrasyonu sayesinde ilk 30 günde gelen müşteri aramaları ve randevu talepleri %45 arttı.\n\n"
                            f"Sistemimizin {biz_name} için nasıl çalışacağını gösteren 2 dakikalık interaktif demo linkini iletmemi ister misiniz?\n\n"
                            f"Görüşmek üzere!"
                        )
                    else:
                        subject = f"Takip: {biz_name} İçin Müşteri Kazanım Otomasyonu & Örnek Vaka ({city})"
                        message = (
                            f"Merhaba {biz_name} Ekibi,\n\n"
                            f"Ben {sender}, {agency}'ndan. Geçtiğimiz günlerde işletmenizin yerel müşteri akışını otomatikleştirecek yazılım ve web çözümlerimiz hakkında kısa bir inceleme notu paylaşmıştım.\n\n"
                            f"Danışanlarımıza kazandırdığımız temel metrikler:\n"
                            f"• Google Harita ve web üzerinden gelen ziyaretçilerin %40+ daha fazla randevuya dönüşmesi\n"
                            f"• 7/24 otomatik WhatsApp karşılama ile mesai dışı müşteri kayıplarının sıfırlanması\n"
                            f"• Hızlı, modern ve Google sıralama uyumlu dijital altyapı\n\n"
                            f"İşletmenize özel hazırladığımız canlı demo linkini ve yol haritasını incelemek ister misiniz?\n\n"
                            f"Saygılarımla,\n{sender}\n{agency}"
                        )
                elif p_type == "custom":
                    if channel == "whatsapp":
                        subject = f"Re: {biz_name} için {prod} teklifi"
                        message = (
                            f"Selamlar {biz_name} yetkilisi! 👋\n\n"
                            f"Ben {sender}, {agency}'ndan. Birkaç gün önce paylaştığım '{prod}' çözümümüzle ilgili kısa bir ekleme yapmak istedim.\n\n"
                            f"Bölgenizdeki iş ortaklarımıza doğrudan toptan/kurumsal fiyat avantajı, hızlı tedarik ve test garantisi sunuyoruz.\n\n"
                            f"1 sayfalık ürün/hizmet özetimizi ve referans listemizi incelemeniz için WhatsApp'tan göndereyim mi?\n\n"
                            f"İyi çalışmalar dilerim!"
                        )
                    else:
                        subject = f"Takip: {biz_name} İçin {prod} Çözüm Detayları & Referanslar"
                        message = (
                            f"Sayın {biz_name} Yetkilisi,\n\n"
                            f"Ben {sender}, {agency}'ndan. Geçtiğimiz günlerde firmanız için paylaştığım '{prod}' konulu iş birliği teklifimize istinaden ulaşıyorum.\n\n"
                            f"Sektördeki iş ortaklarımıza sağladığımız temel avantajlar:\n"
                            f"• Doğrudan kurumsal fiyatlandırma ile anında maliyet avantajı\n"
                            f"• Kesintisiz tedarik ve garantili hizmet güvencesi\n"
                            f"• İhtiyaca özel esnek sipariş ve uygulama modelleri\n\n"
                            f"Konuyla ilgili detaylı ürün/hizmet dokümanımızı incelemek isterseniz bu e-postayı yanıtlamanız yeterlidir.\n\n"
                            f"Saygılarımla,\n{sender}\n{agency}"
                        )
                else:  # general gap-based follow-up
                    gap_key = getattr(lead, "primary_gap", "MISSING_WEBSITE")
                    if channel == "whatsapp":
                        subject = f"Re: {biz_name} dijital büyüme analizi"
                        message = (
                            f"Selamlar {biz_name} yetkilisi! 👋\n\n"
                            f"Ben {sender}, {agency}'ndan. Geçen gün {city} bölgesindeki profilinizi incelerken fark ettiğimiz açıkla ilgili ({gap_key}) kısa bir referans aktarmak istedim.\n\n"
                            f"🎯 Benzer bir işletmede uyguladığımız 1 haftalık optimizasyon sonrasında Google arama görünürlüğü ve gelen müşteri çağrıları 2.4 katına çıktı.\n\n"
                            f"{biz_name} için de hazırladığımız 2 dakikalık aksiyon planını incelemek ister misiniz?\n\n"
                            f"Görüşmek dileğiyle!"
                        )
                    else:
                        subject = f"Takip: {biz_name} İçin Yerel Sıralama & Müşteri Artış Örneği ({city})"
                        message = (
                            f"Sayın {biz_name} Yetkilisi,\n\n"
                            f"Ben {sender}, {agency}'ndan. Birkaç gün önce işletmenizin Google Haritalar görünürlüğü ve müşteri dönüşüm açığı hakkında bir analiz notu iletmiştim.\n\n"
                            f"Bölgenizdeki benzer işletmelerle gerçekleştirdiğimiz çalışmalarda:\n"
                            f"• Yerel arama ve harita sıralamalarında ilk 3 pozisyona yükselme\n"
                            f"• Doğrudan arama ve yol tarifi alan müşteri sayısında %60+ artış sağladık.\n\n"
                            f"{biz_name} için hazırladığımız kısa büyüme planını bu e-postayı 'Evet' olarak yanıtlayarak hemen inceleyebilirsiniz.\n\n"
                            f"Saygılarımla,\n{sender}\n{agency}"
                        )
            else:
                # Step 3: Break-up (Respectful goodbye, low pressure, file closing)
                if p_type == "hair_dye":
                    if channel == "whatsapp":
                        subject = f"{biz_name} kuaför tedarik dosyasını kapatıyorum"
                        message = (
                            f"Merhaba {biz_name} yetkilisi,\n\n"
                            f"Ben {sender}, {agency}'ndan. Çok yoğun bir salon temposunda çalıştığınızı biliyorum, o yüzden gelen kutunuzu daha fazla meşgul etmek istemem.\n\n"
                            f"Salonunuz için toptan saç boyası tedariği ve ücretsiz deneme kiti dosyanızı şimdilik arşive kaldırıyorum. İleride kaliteli ürünleri doğrudan toptan fiyatla temin etmek isterseniz bu mesaja istediğiniz zaman dönebilirsiniz.\n\n"
                            f"Salonunuza bol kazançlı ve bereketli günler dilerim! 🙏"
                        )
                    else:
                        subject = f"İzninizle dosyanızı arşive kaldırıyorum: {biz_name} Salon Tedariği"
                        message = (
                            f"Sayın {biz_name} Yetkilisi,\n\n"
                            f"Ben {sender}, {agency} kurucusuyum. Daha önce ilettiğim toptan saç boyası ve salon sarf malzemeleri tedariği teklifimizle ilgili bir dönüş alamadığımız için dosyanızı kapatıyorum.\n\n"
                            f"Salonunuzun yoğunluğunu çok iyi anlıyorum. İlerleyen süreçte boya maliyetlerini düşürmek ve salon marjınızı artırmak isterseniz bu e-postayı dilediğiniz zaman yanıtlayabilirsiniz.\n\n"
                            f"İşlerinizde başarılar ve bol müşteriler dilerim.\n\n"
                            f"Saygılarımla,\n{sender}\n{agency}"
                        )
                elif p_type == "steam_iron":
                    if channel == "whatsapp":
                        subject = f"{biz_name} sanayi ütü dosyasını kapatıyorum"
                        message = (
                            f"Merhaba {biz_name} yetkilisi,\n\n"
                            f"Ben {sender}, {agency}'ndan. Atölyenizin yoğun imalat ve teslimat temposunu çok iyi biliyorum, bu nedenle vaktinizi daha fazla almayacağım.\n\n"
                            f"Silter sanayi tipi buharlı ütü ve buhar kazanı tesisatı dosyanızı şimdilik kapatıyorum. İleride yeni ütü ihtiyacı, arıza, bakım veya orijinal yedek parça gerektiğinde bana bu numaradan her zaman ulaşabilirsiniz.\n\n"
                            f"Atölyenize bol iş ve kazançlı üretimler dilerim! 🤝"
                        )
                    else:
                        subject = f"İzninizle dosyanızı arşive kaldırıyorum: {biz_name} Buharlı Ütü & Tesisat"
                        message = (
                            f"Sayın {biz_name} Yetkilisi,\n\n"
                            f"Ben {sender}, {agency}'ndan. Tekstil atölyeniz için ilettiğim sanayi tipi buharlı ütü sistemleri ve merkezi kazan tesisatı teklifimiz hakkında dosyanızı kapatıyorum.\n\n"
                            f"Üretim süreçlerinizin yoğunluğunu tahmin edebiliyorum. İleride atölyenizde buhar basıncı yükseltme, yeni tezgah kurulumu veya Silter teknik servis ihtiyacı doğarsa bu e-postayı dilediğiniz zaman yanıtlayabilirsiniz.\n\n"
                            f"Çalışmalarınızda başarılar dilerim.\n\n"
                            f"Saygılarımla,\n{sender}\n{agency}"
                        )
                elif p_type == "software":
                    if channel == "whatsapp":
                        subject = f"{biz_name} yazılım dosyasını kapatıyorum"
                        message = (
                            f"Merhaba {biz_name} yetkilisi,\n\n"
                            f"Ben {sender}, {agency}'ndan. Çok meşgul olduğunuzu anlıyorum, bu yüzden gelen kutunuzu daha fazla meşgul etmemek adına dosyanızı kapatıyorum.\n\n"
                            f"İleride {biz_name} için web sitesi, akıllı randevu veya müşteri otomasyonu kurmak isterseniz bu mesaja her zaman dönüş yapabilirsiniz.\n\n"
                            f"İşletmenize bol kazançlar dilerim! 🙌"
                        )
                    else:
                        subject = f"İzninizle dosyanızı arşive kaldırıyorum: {biz_name} Müşteri Otomasyonu"
                        message = (
                            f"Sayın {biz_name} Yetkilisi,\n\n"
                            f"Ben {sender}, {agency} kurucusuyum. İşletmeniz için ilettiğim dijital yazılım ve müşteri kazanım otomasyonu dosyasını şimdilik kapatıyorum.\n\n"
                            f"Zamanlamanın şu an uygun olmadığını anlıyorum. İlerleyen dönemde işletmenizi dijitalde büyütmek ve müşteri kayıplarını önlemek isterseniz bu e-postayı dilediğiniz zaman yanıtlayabilirsiniz.\n\n"
                            f"Başarılar ve bol kazançlar dilerim.\n\n"
                            f"Saygılarımla,\n{sender}\n{agency}"
                        )
                elif p_type == "custom":
                    if channel == "whatsapp":
                        subject = f"{biz_name} için {prod} dosyasını kapatıyorum"
                        message = (
                            f"Merhaba {biz_name} yetkilisi,\n\n"
                            f"Ben {sender}, {agency}'ndan. Vaktinizi almamak adına '{prod}' ile ilgili dosyanızı kapatıyorum. İleride kurumsal tedarik veya avantajlı fiyat tekliflerimizden yararlanmak isterseniz buradayım.\n\n"
                            f"İşlerinizde başarılar dilerim!"
                        )
                    else:
                        subject = f"İzninizle dosyanızı arşive kaldırıyorum: {biz_name} ({prod})"
                        message = (
                            f"Sayın {biz_name} Yetkilisi,\n\n"
                            f"Ben {sender}, {agency}'ndan. '{prod}' ile ilgili ilettiğim kurumsal teklif dosyanızı şimdilik kapatıyorum.\n\n"
                            f"İleride profesyonel iş birliği veya tedarik maliyetlerini optimize etme ihtiyacı duyduğunuzda kapımız her zaman açık.\n\n"
                            f"Saygılarımla,\n{sender}\n{agency}"
                        )
                else:  # general break-up
                    if channel == "whatsapp":
                        subject = f"{biz_name} dosyasını arşive alıyorum"
                        message = (
                            f"Merhaba {biz_name} yetkilisi,\n\n"
                            f"Ben {sender}, {agency}'ndan. Zamanınızın kıymetli olduğunu biliyorum. Gelen kutunuzu daha fazla meşgul etmemek adına dosyanızı arşive kaldırıyorum.\n\n"
                            f"{city} bölgesinde Google aramalarından daha fazla müşteri çekmek ve cironuzu artırmak istediğinizde bana her zaman buradan ulaşabilirsiniz.\n\n"
                            f"Başarılar ve bol kazançlar dilerim!"
                        )
                    else:
                        subject = f"İzninizle dosyanızı arşive kaldırıyorum: {biz_name}"
                        message = (
                            f"Sayın {biz_name} Yetkilisi,\n\n"
                            f"Ben {sender}, {agency} kurucusuyum. İşletmenizin yerel arama ve harita büyümesiyle ilgili ilettiğim incelememize istinaden dosyanızı kapatıyorum.\n\n"
                            f"Yoğun temponuzu anlıyorum. İleride bölgenizdeki yerel rakiplerinizin önüne geçmek ve düzenli müşteri akışı sağlamak isterseniz bu e-postayı dilediğiniz an yanıtlayabilirsiniz.\n\n"
                            f"Saygılarımla,\n{sender}\n{agency}"
                        )
        else:
            # English versions
            if step == 2:
                # Step 2: English follow-up
                if channel == "whatsapp":
                    subject = f"Quick follow-up for {biz_name}"
                    message = (
                        f"Hey {biz_name} team! 👋\n\n"
                        f"This is {sender} from {agency}. Following up on my previous note regarding growth opportunities for {biz_name} in {city}.\n\n"
                        f"📊 Recent Result: A similar business we supported saw a 45% increase in local inquiries within 30 days of addressing this gap.\n\n"
                        f"Would you like me to share a quick 2-minute breakdown?\n\n"
                        f"Best regards!"
                    )
                else:
                    subject = f"Following up: Growth case study for {biz_name} ({city})"
                    message = (
                        f"Hi {biz_name} Team,\n\n"
                        f"This is {sender} from {agency}. I wanted to quickly follow up on my earlier note regarding customer conversion bottlenecks in {city}.\n\n"
                        f"In our recent engagements with peer businesses, resolving these issues led to a 45% increase in qualified inbound leads within 30 days.\n\n"
                        f"Would you like me to send over our quick 1-page case study?\n\n"
                        f"Best regards,\n{sender}\n{agency}"
                    )
            else:
                # Step 3: English break-up
                if channel == "whatsapp":
                    subject = f"Closing your file for {biz_name}"
                    message = (
                        f"Hi {biz_name} team,\n\n"
                        f"This is {sender} from {agency}. I know you are super busy, so I'll go ahead and close your file to avoid cluttering your inbox.\n\n"
                        f"If you ever want to scale your inbound customer stream in {city}, feel free to reply here anytime.\n\n"
                        f"Wishing you continued success!"
                    )
                else:
                    subject = f"Closing out your file: {biz_name}"
                    message = (
                        f"Dear {biz_name} Team,\n\n"
                        f"This is {sender} from {agency}. I assume the timing isn't right, so I am closing your file and won't reach out further.\n\n"
                        f"If your priorities shift and you wish to explore growing your local customer pipeline in {city}, you can reply to this email anytime.\n\n"
                        f"All the best with your business,\n{sender}\n{agency}"
                    )

        return subject, message

    def _build_wa_link(self, lead: Lead, message: str) -> str:
        if not lead.whatsapp:
            return ""
        encoded_msg = urllib.parse.quote(message)
        if "wa.me/" in lead.whatsapp:
            phone_num = lead.whatsapp.split("wa.me/")[-1].split("?")[0]
            return f"https://wa.me/{phone_num}?text={encoded_msg}"
        return f"{lead.whatsapp}&text={encoded_msg}"

    def _generate_gemini(
        self,
        lead: Lead,
        channel: str,
        tone: str,
        lang: str,
        sender: str,
        agency: str,
        product_pitch_type: str = "general",
        product_name: str = ""
    ) -> Optional[Dict[str, Any]]:
        if not GEMINI_API_KEY:
            return None
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        product_context = ""
        if product_pitch_type == "hair_dye":
            product_context = " Product offered: Wholesale professional hair dye & salon supplies, salon discount tiers, fast shipping, and complimentary sample trial kit."
        elif product_pitch_type == "steam_iron":
            product_context = " Product/Service offered: Industrial steam iron systems (Silter style), central boiler setup, pipeline installation, maintenance, and genuine spare parts for textile workshops and tailors."
        elif product_pitch_type == "software":
            product_context = " Product/Service offered: Custom web & software development, customer acquisition systems, workflow automation, and online appointment/CRM."
        elif product_pitch_type == "custom" and product_name:
            product_context = f" Product/Service offered: {product_name.strip()}."

        prompt = (
            f"Act as an elite B2B sales copywriter. Write a high-converting {tone} {channel} sales pitch for {lead.name} located in {lead.city}. "
            f"Business category: {lead.category}. "
            f"Primary gap: {lead.primary_gap}.{product_context} "
            f"Rating: {lead.rating or 'N/A'}, Reviews: {lead.review_count}. "
            f"Language: {'Turkish' if lang == 'tr' else 'English'}. Sender name: {sender}, Agency: {agency}. "
            f"Respond ONLY with valid JSON having 'subject' and 'content' keys."
        )
        body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = json.loads(resp.read().decode())
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            cleaned = text.strip().replace("```json", "").replace("```", "").strip()
            parsed = json.loads(cleaned)
            content = parsed.get("content", "")
            return {
                "provider": "gemini",
                "channel": channel,
                "tone": tone,
                "language": lang,
                "subject": parsed.get("subject", f"{lead.name} Teklif"),
                "content": content,
                "whatsapp_direct_url": self._build_wa_link(lead, content),
                "primary_gap": lead.primary_gap,
                "product_pitch_type": product_pitch_type,
                "product_name": product_name
            }

    def _generate_openai(
        self,
        lead: Lead,
        channel: str,
        tone: str,
        lang: str,
        sender: str,
        agency: str,
        product_pitch_type: str = "general",
        product_name: str = ""
    ) -> Optional[Dict[str, Any]]:
        if not OPENAI_API_KEY:
            return None
        url = "https://api.openai.com/v1/chat/completions"
        product_context = ""
        if product_pitch_type == "hair_dye":
            product_context = " Product offered: Wholesale professional hair dye & salon supplies, salon discount tiers, fast shipping, and complimentary sample trial kit."
        elif product_pitch_type == "steam_iron":
            product_context = " Product/Service offered: Industrial steam iron systems (Silter style), central boiler setup, pipeline installation, maintenance, and genuine spare parts for textile workshops and tailors."
        elif product_pitch_type == "software":
            product_context = " Product/Service offered: Custom web & software development, customer acquisition systems, workflow automation, and online appointment/CRM."
        elif product_pitch_type == "custom" and product_name:
            product_context = f" Product/Service offered: {product_name.strip()}."

        prompt = (
            f"Write a high-converting {tone} {channel} sales pitch for {lead.name} in {lead.city}. "
            f"Sector: {lead.category}. Primary gap: {lead.primary_gap}.{product_context} "
            f"Rating: {lead.rating or 'N/A'}, Reviews: {lead.review_count}. "
            f"Language: {'Turkish' if lang == 'tr' else 'English'}. Sender: {sender}, Agency: {agency}. "
            f"Output JSON with keys 'subject' and 'content'."
        )
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are an elite B2B sales copywriter and agency growth specialist."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.7
        }
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            }
        )
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = json.loads(resp.read().decode())
            content_str = data["choices"][0]["message"]["content"]
            parsed = json.loads(content_str)
            content = parsed.get("content", "")
            return {
                "provider": "openai",
                "channel": channel,
                "tone": tone,
                "language": lang,
                "subject": parsed.get("subject", f"{lead.name} Teklif"),
                "content": content,
                "whatsapp_direct_url": self._build_wa_link(lead, content),
                "primary_gap": lead.primary_gap,
                "product_pitch_type": product_pitch_type,
                "product_name": product_name
            }

    def _generate_ollama(
        self,
        lead: Lead,
        channel: str,
        tone: str,
        lang: str,
        sender: str,
        agency: str,
        product_pitch_type: str = "general",
        product_name: str = ""
    ) -> Optional[Dict[str, Any]]:
        base_url = (OLLAMA_BASE_URL or "http://localhost:11434").rstrip("/")
        url = f"{base_url}/api/chat"
        product_context = ""
        if product_pitch_type == "hair_dye":
            product_context = " Product offered: Wholesale professional hair dye & salon supplies, salon discount tiers, fast shipping, and complimentary sample trial kit."
        elif product_pitch_type == "steam_iron":
            product_context = " Product/Service offered: Industrial steam iron systems (Silter style), central boiler setup, pipeline installation, maintenance, and genuine spare parts for textile workshops and tailors."
        elif product_pitch_type == "software":
            product_context = " Product/Service offered: Custom web & software development, customer acquisition systems, workflow automation, and online appointment/CRM."
        elif product_pitch_type == "custom" and product_name:
            product_context = f" Product/Service offered: {product_name.strip()}."

        prompt = (
            f"Write a high-converting {tone} {channel} sales pitch for {lead.name} in {lead.city}. "
            f"Sector: {lead.category}. Primary gap: {lead.primary_gap}.{product_context} "
            f"Rating: {lead.rating or 'N/A'}, Reviews: {lead.review_count}. "
            f"Language: {'Turkish' if lang == 'tr' else 'English'}. Sender: {sender}, Agency: {agency}. "
            f"Output JSON with keys 'subject' and 'content'."
        )
        payload = {
            "model": "llama3",
            "messages": [
                {"role": "system", "content": "You are an expert sales copywriter. Respond in JSON with keys 'subject' and 'content'."},
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "format": "json"
        }
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
            data = json.loads(resp.read().decode())
            content_str = data.get("message", {}).get("content", "{}")
            parsed = json.loads(content_str)
            content = parsed.get("content", "")
            return {
                "provider": "ollama",
                "channel": channel,
                "tone": tone,
                "language": lang,
                "subject": parsed.get("subject", f"{lead.name} Teklif"),
                "content": content,
                "whatsapp_direct_url": self._build_wa_link(lead, content),
                "primary_gap": lead.primary_gap,
                "product_pitch_type": product_pitch_type,
                "product_name": product_name
            }


pitch_generator = PitchGenerator()
