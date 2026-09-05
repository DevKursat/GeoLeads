<div align="center">

# 🎯 GeoLeads Pro
### Sıfır Maliyetli B2B Müşteri Bulma, Google Maps Scraper, WhatsApp CRM & Derin Web Açık Denetimi

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![GitHub stars](https://img.shields.io/github/stars/DevKursat/GeoLeads?style=for-the-badge&logo=github&color=amber)](https://github.com/DevKursat/GeoLeads)
[![GitHub forks](https://img.shields.io/github/forks/DevKursat/GeoLeads?style=for-the-badge&logo=github&color=indigo)](https://github.com/DevKursat/GeoLeads/network)

**Google Maps harita verilerini, OpenStreetMap Overpass aynalarını ve DuckDuckGo/Bing yerel dizinlerini 100% gerçek canlı veriyle tarayın; web sitelerinden doğrulanmış e-posta ve WhatsApp hatlarını avlayın; işletmelerin web sitesi açıklarını analiz edip 1-tıkla AI soğuk satış teklifleri üretin!**

[🌟 Projeyi Yıldızla (Star)](https://github.com/DevKursat/GeoLeads) • [🚀 Hızlı Başlangıç](#-hızlı-başlangıç) • [🖥️ Masaüstü Uygulaması](#%EF%B8%8F-masaüstü-uygulaması-desktop) • [🔥 Özellikler](#-temel-özellikler) • [👑 Master Key](#-star-gate--master-key) • [🛠️ Mimari](#%EF%B8%8F-mimari-yapı) • [🌐 About & GEO SEO](#-about-geoleads-seo--geo-growth)

---

</div>

## 💡 Neden GeoLeads Pro?

Geleneksel Google Maps API'leri sorgu başına fahiş faturalar çıkarır veya sadece genel bir santral numarası verir. **GeoLeads**, sıfır maliyetli çoklu arama motorlarıyla (Google Maps, OpenStreetMap Overpass, DuckDuckGo, Bing) **%100 gerçek işletmeleri** bulur:

1. **İşletmenin web sitesine otomatik gider:**
   - İletişim, Hakkımızda ve alt sayfalardan **gerçek e-posta adreslerini** bulur.
   - Doğrudan **WhatsApp hatlarını** ve cep telefonlarını filtreler.
   - Instagram, Facebook, LinkedIn, Twitter sosyal medya profillerini çıkarır.
2. **Satış Açıklarını (Gaps) Otomatik Denetler:**
   - Web sitesi yok mu? **"Web Sitesi Geliştirme & Dönüşüm"** açısı sunar.
   - SSL sertifikası eksik veya güvensiz mi? **"Güvenlik & Güven Açığı"** açısı sunar.
   - Google puanı veya yorum sayısı düşük mü? **"İtibar & Google Harita SEO Yönetimi"** açısı sunar.
   - WhatsApp hızlı iletişim hattı eksik mi? **"WhatsApp Satış Otomasyonu"** açısı sunar.
3. **1-Tıkla AI Kişiselleştirilmiş Satış Kancası Üretir:**
   - İşletmenin adına, şehrine, sektörüne ve **özel açığına** göre hazırlanmış soğuk e-posta ve WhatsApp mesajı oluşturur.
   - Tek tıkla WhatsApp Web'de mesajı doldurur ve gönderime hazır hale getirir.
4. **Entegre Mini CRM Pipeline:**
   - Müşterileri *Yeni Bulunan -> İncelendi -> İletişim Kuruldu -> Görüşmede -> Satış Yapıldı* aşamalarında takip edin.
5. **Masaüstü & Web Çift Modu:**
   - İster tarayıcıda, ister PWA masaüstü uygulaması olarak, isterseniz `./desktop.sh` ile bağımsız masaüstü penceresi olarak kullanın.

---

## 🔥 Temel Özellikler

- 🌐 **%100 Gerçek Canlı Veri (Sıfır Mock / Sentetik Veri Yok):** OpenStreetMap Overpass (5 yedekli döner ayna), Google Maps genel arama ayrıştırıcısı, DuckDuckGo & Bing yerel işletme ayrıştırıcıları ile tamamen gerçek işletmeler.
- 🕷️ **Derin E-Posta & WhatsApp Avcısı:** Web sitelerinin ana sayfası ve `/iletisim`, `/contact`, `/about` sayfalarını tarar; resim/spam e-postalarını eler, net iletişim kanallarını çıkarır.
- ⚡ **Satış Fırsatı Skoru (0 - 100):** Hangi işletmenin dijital hizmete daha çok ihtiyacı olduğunu otomatik puanlar.
- 🤖 **Çoklu AI Desteği & Hazır Şablonlar:** 
  - Google Gemini API
  - OpenAI API
  - Yerel Ollama (Llama 3 / Mistral)
  - **API Anahtarsız Çevrimdışı Yüksek Dönüşümlü Satış Şablonları** (Kutudan çıktığı an çalışır!).
- 📊 **UI/UX Pro Max Arayüz:** Modern Dark/Light tema, cam efekti kartlar (glassmorphism), mikro animasyonlar, filtreler ve çift mod (Tablo & Kanban Pano).
- 🖥️ **PWA & Native Desktop Launcher:** Masaüstü kısayolu, bağımsız pencere modu ve çevrimdışı önbellek desteği.
- 📁 **Excel & CSV Dışa Aktarma:** Türkçe karakterleri (ç, ş, ğ, ö, ü, İ) bozulmadan açan UTF-8 BOM destekli dışa aktarım.

---

## 🖥️ Masaüstü Uygulaması (Desktop)

GeoLeads'i sadece web tarayıcısında değil, bilgisayarınızda **bağımsız bir masaüstü uygulaması** olarak çalıştırabilirsiniz:

### Yöntem A: Native Desktop Penceresi (1 Komutla)
```bash
./desktop.sh
# veya
python3 desktop.py
```
`pywebview` veya tarayıcı app-window modunu kullanarak GeoLeads'i bağımsız, URL çubuğu olmayan yerel masaüstü penceresinde başlatır.

### Yöntem B: PWA Olarak Masaüstüne Yükle
1. GeoLeads'i tarayıcınızda açın (`http://localhost:8000`).
2. Üst menüdeki **"Masaüstüne İndir"** butonuna (veya tarayıcınızın adres çubuğundaki Yükle simgesine) tıklayın.
3. GeoLeads işletim sisteminize (macOS Launchpad, Windows Başlat, Linux Menüsü) yerel bir masaüstü uygulaması olarak eklenecektir.

---

## ⭐ Star-Gate & Organik Büyüme Modeli

GeoLeads, açık kaynak topluluk büyümesini teşvik eden akıllı bir **Star-Gate** mimarisine sahiptir. Hiçbir lisans ücreti veya şifre girme zahmeti olmadan, sadece GitHub depomuza 1 yıldız vererek Pro özelliklerin tamamını açabilirsiniz:

| Özellik | 🌟 Standart Topluluk | ⭐ GitHub Yıldız Destekçisi (1-Tık) |
| :--- | :---: | :---: |
| Arama Başına Müşteri | **25 Adet** | **Sınırsız (500+)** |
| Canlı Harita & OSM Tarama | ✅ | ✅ |
| Sınırsız Excel/CSV İndirme | İlk 25 | ✅ **Sınırsız** |
| Masaüstü Uygulama Modu | ✅ | ✅ |
| Derin E-Posta & WhatsApp Avcısı | Sınırlı | ✅ **Sınırsız Canlı** |
| AI Kişiselleştirilmiş Satış Metni | Önizleme | ✅ **Tam & WhatsApp 1-Tık** |
| Mini CRM Pipeline & Filtreleme | ✅ | ✅ |

> **🌟 Nasıl Açılır?**
> Arayüzdeki veya Star-Gate penceresindeki **"GitHub'da Yıldız Ver & Pro Aç"** butonuna tıklayın. Depo açıldığında yıldız vermenizle birlikte tarayıcınızda tüm Pro özellikler konfeti kutlamasıyla anında aktif olur!
>
> *(İsteğe bağlı: Kendi sunucusunda yönetici olarak çalıştırmak isteyenler için `.env` dosyasında `GEOLEADS_MASTER_KEY` ayarlanabilir).*

---

## 🚀 Hızlı Başlangıç

### Yöntem 1: Yerel Çalıştırma (1 Komutla, Sıfır Kurulum)

Python 3.9+ yüklü olması yeterlidir:

```bash
git clone https://github.com/DevKursat/GeoLeads.git
cd GeoLeads

# Web arayüzü için:
./start.sh

# Masaüstü uygulaması için:
./desktop.sh
```

Tarayıcınızda açın: **`http://localhost:8000`**

### Yöntem 2: Docker Compose ile

```bash
docker compose up --build
```

---

## 🛠️ Mimari Yapı

```
GeoLeads/
├── desktop.py                    # Masaüstü yerel pencere başlatıcı
├── desktop.sh                    # Masaüstü tek tıkla çalıştırma betiği
├── start.sh                      # Web sunucu başlatma betiği
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py         # Çevre değişkenleri & Master Key güvenliği
│   │   │   └── database.py       # SQLite & CRUD işlemleri
│   │   ├── services/
│   │   │   ├── scraper_engine.py # OSM Overpass, Google Maps, DDG & Bing tarayıcı
│   │   │   ├── website_crawler.py# Derin web sitesi, e-posta & WhatsApp avcısı
│   │   │   ├── gap_detector.py   # Satış açıkları & Fırsat skorlama
│   │   │   ├── pitch_generator.py# AI & Şablon soğuk satış metinleri
│   │   │   └── export_service.py # UTF-8 BOM CSV / Excel dışa aktarım
│   │   ├── models.py             # Veri modelleri & Enums
│   │   └── main.py               # REST API & Statik dosya sunucusu
│   ├── static/
│   │   ├── index.html            # UI/UX Pro Max Arayüzü (SEO, Tailwind, Lucide)
│   │   ├── manifest.json         # PWA Masaüstü Manifesti
│   │   ├── sw.js                 # PWA Service Worker (Çevrimdışı önbellek)
│   │   └── icon.svg              # Masaüstü uygulama ikonu
│   ├── tests/                    # Otomatik test süiti (31/31 Geçer)
│   └── server.py                 # Sunucu başlatıcı
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── .env.example
└── README.md
```

---

## 🧪 Testleri Çalıştırma

GeoLeads, kapsamlı bir test süitine sahiptir:

```bash
python3 -m unittest discover -s backend/tests -p "test_*.py" -v
```

Sonuç: **Tüm 38 test başarıyla geçmektedir.**

---

## 🌐 About GeoLeads, SEO & GEO Growth

### 🎯 Hakkında & Sıfır Maliyetli Küresel GEO Mimarisi

**GeoLeads**, geleneksel B2B müşteri bulma servislerinin ve Google Maps API'lerinin dayattığı sorgu başına fahiş maliyetlere ve kapalı veri modellerine karşı geliştirilmiş **%100 açık kaynaklı** bir lead motorudur.

#### 🌍 GEO & Küresel Yerel Arama Nasıl Çalışır?
- **Çoklu Arama Motoru Fallback Hibriti:** Hedef lokasyon için önce 5 döner aynalı **OpenStreetMap Overpass** ağı taranır. Ardından **Google Maps Canlı Web Ayrıştırıcısı**, **DuckDuckGo Local** ve **Bing Yerel İşletmeler** dizinleri eşzamanlı harmanlanır.
- **Sınırsız Coğrafi Kapsama (GEO Targeting):** Şehir veya ilçe bazında (örn. *İstanbul Kadıköy Diş Klinikleri*, *Berlin Kreuzberg Cafes*, *London Westminster Accountants*, *New York Brooklyn Law Firms*) tam coğrafi sınır koordinatları ve yerel dizinler taranır.
- **Derin Web E-Posta & WhatsApp Avcısı:** İşletmenin web sitesine otomatik gidilerek ana sayfa ve `/iletisim`, `/contact`, `/about` alt sayfalarından kurumsal e-postalar ve doğrudan WhatsApp hatları ayıklanır.
- **Dijital Satış Açığı & Fırsat Skoru (0-100):** Web sitesi eksikliği, SSL sertifikası yokluğu, düşük Google değerlendirmesi gibi satış kancaları tespit edilerek tek tıkla AI soğuk satış teklifi üretilir.

---

### 📈 Star History (Yıldız Geçmişi)

Projeye yıldız vererek açık kaynak geliştiricilere destek olun ve büyüme grafiğimizi takip edin:

[![Star History Chart](https://api.star-history.com/svg?repos=DevKursat/GeoLeads&type=Date)](https://star-history.com/#DevKursat/GeoLeads&Date)

---

### 🏷️ Önerilen GitHub Depo "About" Ayarları (SEO & Organik Sıralama)

GitHub arama motoru, explore sayfası ve Google SERP sıralamalarında zirveye yerleşmek için GitHub Depo Ayarları (`Settings -> About`) bölümüne aşağıdaki bilgileri doğrudan kopyalayıp yapıştırabilirsiniz:

#### 1. Repository Description (Depo Açıklaması - 350 Karakter):
```text
🎯 Sıfır maliyetli Google Maps & Yerel İşletme B2B Müşteri Bulma Motoru. Haritalardan canlı işletmeleri tara, derin web avcısıyla e-posta & WhatsApp bul, AI ile kişiselleştirilmiş soğuk satış teklifi üret! Zero-cost Google Maps Scraper, Lead Generation, Web Audit & Cold Outreach CRM.
```

#### 2. Website / Homepage URL:
```text
https://github.com/DevKursat/GeoLeads
```

#### 3. 20 Yüksek Sıralamalı Konu Etiketi (GitHub Topics / Tags):
> *GitHub repo ayarlarındaki "Topics" alanına virgülle veya tek tek yapıştırın:*

```text
google-maps-scraper, lead-generation, b2b-leads, cold-outreach, whatsapp-crm, email-scraper, local-seo, geo-targeting, openstreetmap, overpass-api, fastapi, python-scraper, business-intelligence, sales-automation, growth-hacking, web-scraping, marketing-tools, crm, b2b-sales, google-maps-api-alternative
```

#### 🔍 Neden Bu Etiketler?
1. **GitHub Explore & Trending İndeksi:** `lead-generation`, `google-maps-scraper` ve `web-scraping` etiketleri dünya genelinde haftalık on binlerce yazılımcı ve ajans tarafından taranmaktadır.
2. **Google SEO Backlink & Arama İndeksi:** Bu anahtar kelimeler, arama motorlarında "free google maps scraper without api key" ve "python b2b lead generator" sorgularında depomuzun 1. sayfada indekslenmesini sağlar.
3. **GEO Hedefli Dönüşüm:** `geo-targeting`, `local-seo` ve `openstreetmap` etiketleri yerel pazarlama uzmanlarını doğrudan projeye çeker.

---

## 🌟 GitHub Star Desteği

GeoLeads, açık kaynak topluluk büyümesi ile B2B ajansların, serbest çalışanların (freelance) ve yazılımcıların müşteri bulma derdine son vermek için inşa edilmiştir.

Projeyi faydalı bulduysanız lütfen bir **⭐ Star** vererek açık kaynak topluluğumuza destek olun!

[https://github.com/DevKursat/GeoLeads](https://github.com/DevKursat/GeoLeads)

---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır. Ticari ve kişisel kullanım için tamamen serbesttir.
