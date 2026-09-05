"""
Database manager for GeoLeads using SQLite.
Self-contained, thread-safe, and robust.
"""
import sqlite3
import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.core.config import DB_FILE
from app.models import Lead, CRMStage


class Database:
    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        with self.get_connection() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                place_id TEXT UNIQUE,
                name TEXT NOT NULL,
                category TEXT,
                city TEXT,
                address TEXT,
                latitude REAL,
                longitude REAL,
                phone TEXT,
                website TEXT,
                rating REAL,
                review_count INTEGER DEFAULT 0,
                google_maps_url TEXT,
                emails TEXT,           -- JSON array
                phones TEXT,           -- JSON array
                whatsapp TEXT,
                instagram TEXT,
                facebook TEXT,
                linkedin TEXT,
                twitter TEXT,
                youtube TEXT,
                has_website INTEGER DEFAULT 0,
                has_ssl INTEGER DEFAULT 0,
                meta_title TEXT,
                meta_description TEXT,
                opportunity_score INTEGER DEFAULT 0,
                gaps TEXT,             -- JSON array
                primary_gap TEXT,
                crm_stage TEXT DEFAULT 'NEW',
                notes TEXT DEFAULT '',
                last_contacted_at TEXT,
                created_at TEXT,
                updated_at TEXT
            );
            """)

            conn.execute("""
            CREATE TABLE IF NOT EXISTS searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                city TEXT,
                count INTEGER DEFAULT 0,
                is_pro INTEGER DEFAULT 0,
                created_at TEXT
            );
            """)

            conn.execute("""
            CREATE TABLE IF NOT EXISTS notes_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id INTEGER,
                content TEXT,
                created_at TEXT,
                FOREIGN KEY (lead_id) REFERENCES leads (id) ON DELETE CASCADE
            );
            """)
            conn.commit()

    def save_or_update_lead(self, lead: Lead) -> Lead:
        with self.get_connection() as conn:
            # Normalize place_id
            place_id = lead.place_id if lead.place_id else None

            # Check if exists by place_id or name+city
            existing = None
            if place_id:
                cursor = conn.execute("SELECT id FROM leads WHERE place_id = ?", (place_id,))
                existing = cursor.fetchone()
            if not existing and lead.name and lead.city:
                cursor = conn.execute("SELECT id FROM leads WHERE name = ? AND city = ?", (lead.name, lead.city))
                existing = cursor.fetchone()

            emails_json = json.dumps(lead.emails)
            phones_json = json.dumps(lead.phones)
            gaps_json = json.dumps([g.to_dict() for g in lead.gaps])
            now_iso = datetime.utcnow().isoformat()

            if existing:
                lead_id = existing["id"]
                conn.execute("""
                UPDATE leads SET
                    name = ?, category = ?, city = ?, address = ?, latitude = ?, longitude = ?,
                    phone = ?, website = ?, rating = ?, review_count = ?, google_maps_url = ?,
                    emails = ?, phones = ?, whatsapp = ?, instagram = ?, facebook = ?,
                    linkedin = ?, twitter = ?, youtube = ?, has_website = ?, has_ssl = ?,
                    meta_title = ?, meta_description = ?, opportunity_score = ?, gaps = ?,
                    primary_gap = ?, updated_at = ?
                WHERE id = ?
                """, (
                    lead.name, lead.category, lead.city, lead.address, lead.latitude, lead.longitude,
                    lead.phone, lead.website, lead.rating, lead.review_count, lead.google_maps_url,
                    emails_json, phones_json, lead.whatsapp, lead.instagram, lead.facebook,
                    lead.linkedin, lead.twitter, lead.youtube, 1 if lead.has_website else 0,
                    1 if lead.has_ssl else 0, lead.meta_title, lead.meta_description,
                    lead.opportunity_score, gaps_json, lead.primary_gap, now_iso, lead_id
                ))
                lead.id = lead_id
            else:
                cursor = conn.execute("""
                INSERT INTO leads (
                    place_id, name, category, city, address, latitude, longitude,
                    phone, website, rating, review_count, google_maps_url,
                    emails, phones, whatsapp, instagram, facebook,
                    linkedin, twitter, youtube, has_website, has_ssl,
                    meta_title, meta_description, opportunity_score, gaps,
                    primary_gap, crm_stage, notes, last_contacted_at, created_at, updated_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?
                )
                """, (
                    place_id, lead.name, lead.category, lead.city, lead.address, lead.latitude, lead.longitude,
                    lead.phone, lead.website, lead.rating, lead.review_count, lead.google_maps_url,
                    emails_json, phones_json, lead.whatsapp, lead.instagram, lead.facebook,
                    lead.linkedin, lead.twitter, lead.youtube, 1 if lead.has_website else 0,
                    1 if lead.has_ssl else 0, lead.meta_title, lead.meta_description,
                    lead.opportunity_score, gaps_json, lead.primary_gap,
                    lead.crm_stage.value, lead.notes, lead.last_contacted_at, now_iso, now_iso
                ))
                lead.id = cursor.lastrowid

            conn.commit()
            return lead

    def get_lead(self, lead_id: int) -> Optional[Lead]:
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_lead(row)

    def list_leads(
        self,
        category: Optional[str] = None,
        city: Optional[str] = None,
        crm_stage: Optional[str] = None,
        min_opportunity: Optional[int] = None,
        search_term: Optional[str] = None,
        limit: int = 200,
        offset: int = 0
    ) -> List[Lead]:
        with self.get_connection() as conn:
            query = "SELECT * FROM leads WHERE 1=1"
            params: List[Any] = []

            if category:
                query += " AND category LIKE ?"
                params.append(f"%{category}%")
            if city:
                query += " AND city LIKE ?"
                params.append(f"%{city}%")
            if crm_stage:
                query += " AND crm_stage = ?"
                params.append(crm_stage)
            if min_opportunity is not None:
                query += " AND opportunity_score >= ?"
                params.append(min_opportunity)
            if search_term:
                query += " AND (name LIKE ? OR address LIKE ? OR phone LIKE ?)"
                params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])

            query += " ORDER BY id DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor = conn.execute(query, params)
            return [self._row_to_lead(row) for row in cursor.fetchall()]

    def update_crm_stage(self, lead_id: int, stage: CRMStage, notes: Optional[str] = None) -> bool:
        with self.get_connection() as conn:
            now_iso = datetime.utcnow().isoformat()
            if notes is not None:
                conn.execute(
                    "UPDATE leads SET crm_stage = ?, notes = ?, updated_at = ? WHERE id = ?",
                    (stage.value, notes, now_iso, lead_id)
                )
            else:
                conn.execute(
                    "UPDATE leads SET crm_stage = ?, updated_at = ? WHERE id = ?",
                    (stage.value, now_iso, lead_id)
                )
            conn.commit()
            return True

    def record_contact(self, lead_id: int, channel: str = "whatsapp") -> bool:
        with self.get_connection() as conn:
            now_iso = datetime.utcnow().isoformat()
            conn.execute(
                "UPDATE leads SET crm_stage = 'CONTACTED', last_contacted_at = ?, updated_at = ? WHERE id = ?",
                (now_iso, now_iso, lead_id)
            )
            conn.commit()
            return True

    def delete_lead(self, lead_id: int) -> bool:
        with self.get_connection() as conn:
            conn.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
            conn.commit()
            return True

    def get_stats(self) -> Dict[str, Any]:
        with self.get_connection() as conn:
            total_leads = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
            with_email = conn.execute("SELECT COUNT(*) FROM leads WHERE emails != '[]' AND emails IS NOT NULL").fetchone()[0]
            with_phone = conn.execute("SELECT COUNT(*) FROM leads WHERE phone != '' AND phone IS NOT NULL").fetchone()[0]
            with_whatsapp = conn.execute("SELECT COUNT(*) FROM leads WHERE whatsapp != '' AND whatsapp IS NOT NULL").fetchone()[0]
            missing_website = conn.execute("SELECT COUNT(*) FROM leads WHERE has_website = 0").fetchone()[0]
            high_opportunity = conn.execute("SELECT COUNT(*) FROM leads WHERE opportunity_score >= 70").fetchone()[0]

            # Stage counts
            stages = {}
            for stage in CRMStage:
                count = conn.execute("SELECT COUNT(*) FROM leads WHERE crm_stage = ?", (stage.value,)).fetchone()[0]
                stages[stage.value] = count

            return {
                "total_leads": total_leads,
                "with_email": with_email,
                "with_phone": with_phone,
                "with_whatsapp": with_whatsapp,
                "missing_website": missing_website,
                "high_opportunity": high_opportunity,
                "pipeline_stages": stages
            }

    def _row_to_lead(self, row: sqlite3.Row) -> Lead:
        d = dict(row)
        d["emails"] = json.loads(d.get("emails") or "[]")
        d["phones"] = json.loads(d.get("phones") or "[]")
        d["gaps"] = json.loads(d.get("gaps") or "[]")
        return Lead.from_dict(d)


db = Database()
