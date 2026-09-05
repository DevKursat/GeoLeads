"""
Main API router and server entrypoint for GeoLeads.
Supports both FastAPI (when installed) and native Python HTTP server.
"""
import json
import os
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, List, Optional

from app.core.config import (
    MASTER_KEY, COMMUNITY_MAX_LEADS_PER_SEARCH, PRO_MAX_LEADS_PER_SEARCH,
    GITHUB_REPO_URL
)
from app.core.database import db
from app.models import Lead, CRMStage
from app.services.scraper_engine import scraper_engine
from app.services.pitch_generator import pitch_generator
from app.services.export_service import export_service

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")


def check_is_master(headers_dict: Dict[str, str], body_dict: Optional[Dict[str, Any]] = None) -> bool:
    """Checks if request has valid master key in headers or body."""
    auth_header = headers_dict.get("x-master-key", "")
    if auth_header and auth_header == MASTER_KEY:
        return True
    if body_dict and body_dict.get("master_key") == MASTER_KEY:
        return True
    return False


class GeoLeadsRequestHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Master-Key, Authorization")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/api/stats":
            stats = db.get_stats()
            self._send_json(200, {
                "success": True,
                "data": stats,
                "limits": {
                    "community_max": COMMUNITY_MAX_LEADS_PER_SEARCH,
                    "pro_max": PRO_MAX_LEADS_PER_SEARCH
                }
            })

        elif path == "/api/leads":
            category = query.get("category", [None])[0]
            city = query.get("city", [None])[0]
            crm_stage = query.get("crm_stage", [None])[0]
            min_opp = int(query.get("min_opportunity", [0])[0]) if query.get("min_opportunity") else None
            search = query.get("search", [None])[0]
            limit = int(query.get("limit", [100])[0])
            offset = int(query.get("offset", [0])[0])

            leads = db.list_leads(
                category=category,
                city=city,
                crm_stage=crm_stage,
                min_opportunity=min_opp,
                search_term=search,
                limit=limit,
                offset=offset
            )
            self._send_json(200, {
                "success": True,
                "total": len(leads),
                "data": [l.to_dict() for l in leads]
            })

        elif path.startswith("/api/leads/") and not path.endswith("/pitch"):
            try:
                lead_id = int(path.split("/")[-1])
                lead = db.get_lead(lead_id)
                if not lead:
                    self._send_json(404, {"success": False, "error": "Lead not found"})
                else:
                    self._send_json(200, {"success": True, "data": lead.to_dict()})
            except ValueError:
                self._send_json(400, {"success": False, "error": "Invalid lead ID"})

        elif path == "/api/export/csv":
            category = query.get("category", [None])[0]
            city = query.get("city", [None])[0]
            crm_stage = query.get("crm_stage", [None])[0]
            leads = db.list_leads(category=category, city=city, crm_stage=crm_stage, limit=1000)
            csv_content = export_service.export_csv(leads)

            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", 'attachment; filename="geoleads_export.csv"')
            self.end_headers()
            self.wfile.write(csv_content.encode("utf-8"))

        elif path == "/api/system/health":
            self._send_json(200, {
                "status": "healthy",
                "version": "1.0.0-pro",
                "github_repo": GITHUB_REPO_URL,
                "community_lead_limit": COMMUNITY_MAX_LEADS_PER_SEARCH
            })

        else:
            # Serve static files or index.html
            self._serve_static(path)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self._read_json_body()

        headers_lower = {k.lower(): v for k, v in self.headers.items()}
        is_pro = check_is_master(headers_lower, body)

        if path == "/api/auth/verify-master":
            key = body.get("key", "")
            is_valid = (key == MASTER_KEY)
            self._send_json(200, {
                "is_valid": is_valid,
                "pro_unlocked": is_valid,
                "message": "Superuser Pro Mode Active" if is_valid else "Invalid Master Key"
            })

        elif path == "/api/scrape":
            query_str = body.get("query", "").strip()
            city_str = body.get("city", "").strip()
            requested_leads = int(body.get("max_leads", 20))
            deep_crawl = bool(body.get("deep_crawl", True))

            if not query_str or not city_str:
                self._send_json(400, {"success": False, "error": "Query and City are required"})
                return

            star_gate_triggered = False
            effective_limit = requested_leads

            if not is_pro:
                if requested_leads > COMMUNITY_MAX_LEADS_PER_SEARCH:
                    effective_limit = COMMUNITY_MAX_LEADS_PER_SEARCH
                    star_gate_triggered = True

            leads = scraper_engine.search_and_enrich(
                query=query_str,
                city=city_str,
                max_leads=effective_limit,
                deep_crawl=deep_crawl
            )

            self._send_json(200, {
                "success": True,
                "count": len(leads),
                "is_pro": is_pro,
                "star_gate_triggered": star_gate_triggered,
                "data": [l.to_dict() for l in leads]
            })

        elif path.startswith("/api/leads/") and path.endswith("/stage"):
            try:
                parts = path.split("/")
                lead_id = int(parts[3])
                stage_str = body.get("stage", "NEW")
                notes = body.get("notes")
                stage = CRMStage(stage_str)
                db.update_crm_stage(lead_id, stage, notes)
                self._send_json(200, {"success": True, "lead_id": lead_id, "crm_stage": stage.value})
            except Exception as e:
                self._send_json(400, {"success": False, "error": str(e)})

        elif path.startswith("/api/leads/") and path.endswith("/contact"):
            try:
                parts = path.split("/")
                lead_id = int(parts[3])
                channel = body.get("channel", "whatsapp")
                db.record_contact(lead_id, channel)
                self._send_json(200, {"success": True, "lead_id": lead_id, "status": "CONTACTED"})
            except Exception as e:
                self._send_json(400, {"success": False, "error": str(e)})

        elif path.startswith("/api/leads/") and path.endswith("/pitch"):
            try:
                parts = path.split("/")
                lead_id = int(parts[3])
                lead = db.get_lead(lead_id)
                if not lead:
                    self._send_json(404, {"success": False, "error": "Lead not found"})
                    return

                channel = body.get("channel", "whatsapp")
                tone = body.get("tone", "consultative")
                lang = body.get("lang", "tr")
                sender = body.get("sender_name", "Kürşat")
                agency = body.get("agency_name", "Dijital Büyüme Ajansı")

                pitch = pitch_generator.generate_pitch(
                    lead=lead,
                    channel=channel,
                    tone=tone,
                    lang=lang,
                    custom_sender_name=sender,
                    custom_agency_name=agency
                )
                self._send_json(200, {"success": True, "data": pitch})
            except Exception as e:
                self._send_json(400, {"success": False, "error": str(e)})

        else:
            self._send_json(404, {"success": False, "error": "Route not found"})

    def _send_json(self, status_code: int, data: Dict[str, Any]):
        response_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def _read_json_body(self) -> Dict[str, Any]:
        content_len = int(self.headers.get("content-length", 0))
        if content_len == 0:
            return {}
        try:
            raw = self.rfile.read(content_len).decode("utf-8")
            return json.loads(raw)
        except Exception:
            return {}

    def _serve_static(self, path: str):
        if path == "/" or path == "":
            file_path = os.path.join(STATIC_DIR, "index.html")
        else:
            clean_path = path.lstrip("/")
            file_path = os.path.join(STATIC_DIR, clean_path)

        if not os.path.exists(file_path) or os.path.isdir(file_path):
            file_path = os.path.join(STATIC_DIR, "index.html")

        if os.path.exists(file_path):
            mime_type = "text/html"
            if file_path.endswith(".css"):
                mime_type = "text/css"
            elif file_path.endswith(".js"):
                mime_type = "application/javascript"
            elif file_path.endswith(".json"):
                mime_type = "application/json"
            elif file_path.endswith(".png"):
                mime_type = "image/png"
            elif file_path.endswith(".svg"):
                mime_type = "image/svg+xml"

            with open(file_path, "rb") as f:
                content = f.read()

            self.send_response(200)
            self.send_header("Content-Type", f"{mime_type}; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self._send_json(404, {"error": "File not found"})

    def log_message(self, format, *args):
        # Suppress noisy standard request logs
        return


def run_server(port: int = 8000, host: str = "0.0.0.0"):
    server_address = (host, port)
    httpd = HTTPServer(server_address, GeoLeadsRequestHandler)
    print(f" GeoLeads Production Server running on http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping GeoLeads server...")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
