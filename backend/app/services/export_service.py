"""
Export service for GeoLeads.
Exports leads to Excel-ready CSV (with UTF-8 BOM) and structured JSON.
"""
import csv
import io
from typing import List
from app.models import Lead


class ExportService:
    @staticmethod
    def export_csv(leads: List[Lead]) -> str:
        """
        Generates CSV string with UTF-8 BOM so Excel opens Turkish and international characters properly.
        """
        output = io.StringIO()
        # UTF-8 BOM
        output.write('\ufeff')

        writer = csv.writer(output, delimiter=',', quoting=csv.QUOTE_MINIMAL)

        # Header
        headers = [
            "ID", "İşletme Adı", "Kategori", "Şehir", "Adres", "Telefon", "E-postalar",
            "Web Sitesi", "Google Puanı", "Yorum Sayısı", "Fırsat Puanı (100)",
            "Tespit Edilen Açıklar", "Öncelikli Satış Kancası", "WhatsApp Linki",
            "Instagram", "Facebook", "LinkedIn", "CRM Durumu", "Google Harita Linki", "Notlar"
        ]
        writer.writerow(headers)

        for l in leads:
            emails_str = "; ".join(l.emails)
            gaps_str = "; ".join([g.title for g in l.gaps])
            writer.writerow([
                l.id or "",
                l.name,
                l.category,
                l.city,
                l.address,
                l.phone,
                emails_str,
                l.website,
                l.rating if l.rating is not None else "",
                l.review_count,
                l.opportunity_score,
                gaps_str,
                l.primary_gap,
                l.whatsapp,
                l.instagram,
                l.facebook,
                l.linkedin,
                l.crm_stage.value,
                l.google_maps_url,
                l.notes
            ])

        return output.getvalue()


export_service = ExportService()
