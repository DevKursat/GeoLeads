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
            master_param = query.get("master_key", [None])[0] or query.get("x-master-key", [None])[0]
            starred_param = query.get("starred", [None])[0] or query.get("x-starred", [None])[0]
            headers_lower = {k.lower(): v for k, v in self.headers.items()}
            is_starred = (headers_lower.get("x-starred") == "1") or (starred_param in ["1", "true", "True"])
            is_pro = check_is_master(headers_lower) or (master_param == MASTER_KEY) or is_starred
            export_limit = 10000 if is_pro else COMMUNITY_MAX_LEADS_PER_SEARCH
            leads = db.list_leads(category=category, city=city, crm_stage=crm_stage, limit=export_limit)
            csv_content = export_service.export_csv(leads)

            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", 'attachment; filename="geoleads_export.csv"')
            self.send_header("X-Is-Pro", "1" if is_pro else "0")
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

            is_starred = (headers_lower.get("x-starred") == "1") or bool(body.get("is_starred", False))
            star_gate_triggered = False
            effective_limit = requested_leads

            max_community = PRO_MAX_LEADS_PER_SEARCH if is_starred else COMMUNITY_MAX_LEADS_PER_SEARCH

            if not is_pro and not is_starred:
                if requested_leads > max_community:
                    effective_limit = max_community
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
                "is_pro": is_pro or is_starred,
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

                # Star-Gate enforcement: non-pro users can preview 1 lead pitch if preview requested,
                # otherwise prompts for GitHub Star
                is_starred = (headers_lower.get("x-starred") == "1") or bool(body.get("is_starred", False))
                is_preview = bool(body.get("is_preview", False))
                has_full_access = is_pro or is_starred

                if not has_full_access and not is_preview:
                    self._send_json(403, {
                        "success": False,
                        "star_gate_required": True,
                        "error": "Bu özellik GitHub Yıldız Destekçilerine özeldir. AI Satış Kancalarını açmak için lütfen depoya yıldız verin!",
                        "github_repo": GITHUB_REPO_URL
                    })
                    return

                channel = body.get("channel", "whatsapp")
                tone = body.get("tone", "consultative")
                lang = body.get("lang", "tr")
                sender = body.get("sender_name", "Kürşat")
                agency = body.get("agency_name", "Dijital Büyüme Ajansı")
                product_pitch_type = body.get("product_pitch_type", "general")
                product_name = body.get("product_name", "")
                sequence_step = int(body.get("sequence_step", 1) or 1)
                roi_metrics = body.get("roi_metrics")

                pitch = pitch_generator.generate_pitch(
                    lead=lead,
                    channel=channel,
                    tone=tone,
                    lang=lang,
                    custom_sender_name=sender,
                    custom_agency_name=agency,
                    product_pitch_type=product_pitch_type,
                    product_name=product_name,
                    sequence_step=sequence_step,
                    roi_metrics=roi_metrics
                )
                if not has_full_access:
                    pitch["content"] += "\n\n[ GeoLeads Topluluk Önizlemesi - Sınırsız AI ve Otomatik CRM için GitHub'da Yıldız Verin]"

                self._send_json(200, {
                    "success": True,
                    "is_pro": has_full_access,
                    "star_gate_required": not has_full_access,
                    "data": pitch
                })
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


# Optional FastAPI Application export for ASGI servers (e.g. uvicorn app.main:app)
try:
    from fastapi import FastAPI, Header
    from fastapi.responses import JSONResponse, Response
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False


def create_fastapi_app():
    if not HAS_FASTAPI:
        return None
    fastapi_app = FastAPI(
        title="GeoLeads Pro API",
        version="1.0.0-pro",
        description="Autonomous B2B Lead Scraping Engine, Sales Gap Auditor & Mini CRM"
    )
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    @fastapi_app.get("/api/system/health")
    async def health():
        return {
            "status": "healthy",
            "version": "1.0.0-pro",
            "github_repo": GITHUB_REPO_URL,
            "community_lead_limit": COMMUNITY_MAX_LEADS_PER_SEARCH
        }

    @fastapi_app.get("/api/stats")
    async def get_stats():
        return {
            "success": True,
            "data": db.get_stats(),
            "limits": {
                "community_max": COMMUNITY_MAX_LEADS_PER_SEARCH,
                "pro_max": PRO_MAX_LEADS_PER_SEARCH
            }
        }

    @fastapi_app.get("/api/leads")
    async def list_leads(
        category: Optional[str] = None,
        city: Optional[str] = None,
        crm_stage: Optional[str] = None,
        min_opportunity: Optional[int] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ):
        leads = db.list_leads(
            category=category,
            city=city,
            crm_stage=crm_stage,
            min_opportunity=min_opportunity,
            search_term=search,
            limit=limit,
            offset=offset
        )
        return {"success": True, "total": len(leads), "data": [l.to_dict() for l in leads]}

    @fastapi_app.get("/api/leads/{lead_id}")
    async def get_lead(lead_id: int):
        lead = db.get_lead(lead_id)
        if not lead:
            return JSONResponse(status_code=404, content={"success": False, "error": "Lead not found"})
        return {"success": True, "data": lead.to_dict()}

    @fastapi_app.post("/api/auth/verify-master")
    async def verify_master(payload: dict):
        key = payload.get("key", "")
        is_valid = (key == MASTER_KEY)
        return {
            "is_valid": is_valid,
            "pro_unlocked": is_valid,
            "message": "Superuser Pro Mode Active" if is_valid else "Invalid Master Key"
        }

    @fastapi_app.post("/api/scrape")
    async def scrape(
        payload: dict,
        x_master_key: Optional[str] = Header(None),
        x_starred: Optional[str] = Header(None)
    ):
        query_str = payload.get("query", "").strip()
        city_str = payload.get("city", "").strip()
        requested_leads = int(payload.get("max_leads", 20))
        deep_crawl = bool(payload.get("deep_crawl", True))

        if not query_str or not city_str:
            return JSONResponse(status_code=400, content={"success": False, "error": "Query and City are required"})

        is_pro = (x_master_key == MASTER_KEY or payload.get("master_key") == MASTER_KEY)
        is_starred = (x_starred == "1" or bool(payload.get("is_starred", False)))
        star_gate_triggered = False
        effective_limit = requested_leads

        max_community = PRO_MAX_LEADS_PER_SEARCH if is_starred else COMMUNITY_MAX_LEADS_PER_SEARCH

        if not is_pro and not is_starred:
            if requested_leads > max_community:
                effective_limit = max_community
                star_gate_triggered = True

        leads = scraper_engine.search_and_enrich(
            query=query_str,
            city=city_str,
            max_leads=effective_limit,
            deep_crawl=deep_crawl
        )
        return {
            "success": True,
            "count": len(leads),
            "is_pro": is_pro or is_starred,
            "star_gate_triggered": star_gate_triggered,
            "data": [l.to_dict() for l in leads]
        }

    @fastapi_app.post("/api/leads/{lead_id}/stage")
    async def update_stage(lead_id: int, payload: dict):
        stage = CRMStage(payload.get("stage", "NEW"))
        db.update_crm_stage(lead_id, stage, payload.get("notes"))
        return {"success": True, "lead_id": lead_id, "crm_stage": stage.value}

    @fastapi_app.post("/api/leads/{lead_id}/pitch")
    async def create_pitch(
        lead_id: int,
        payload: dict,
        x_master_key: Optional[str] = Header(None),
        x_starred: Optional[str] = Header(None)
    ):
        lead = db.get_lead(lead_id)
        if not lead:
            return JSONResponse(status_code=404, content={"success": False, "error": "Lead not found"})
        is_pro = (x_master_key == MASTER_KEY or payload.get("master_key") == MASTER_KEY)
        is_starred = (x_starred == "1" or bool(payload.get("is_starred", False)))
        is_preview = bool(payload.get("is_preview", False))
        has_full_access = is_pro or is_starred

        if not has_full_access and not is_preview:
            return JSONResponse(status_code=403, content={
                "success": False,
                "star_gate_required": True,
                "error": "Bu özellik GitHub Yıldız Destekçilerine özeldir. AI Satış Kancalarını açmak için depoya yıldız verin!",
                "github_repo": GITHUB_REPO_URL
            })
        pitch = pitch_generator.generate_pitch(
            lead=lead,
            channel=payload.get("channel", "whatsapp"),
            tone=payload.get("tone", "consultative"),
            lang=payload.get("lang", "tr"),
            custom_sender_name=payload.get("sender_name", "Kürşat"),
            custom_agency_name=payload.get("agency_name", "Dijital Büyüme Ajansı"),
            product_pitch_type=payload.get("product_pitch_type", "general"),
            product_name=payload.get("product_name", ""),
            sequence_step=int(payload.get("sequence_step", 1) or 1),
            roi_metrics=payload.get("roi_metrics")
        )
        if not has_full_access:
            pitch["content"] += "\n\n[ GeoLeads Topluluk Önizlemesi - Sınırsız AI ve Otomatik CRM için GitHub'da Yıldız Verin]"
        return {"success": True, "is_pro": has_full_access, "star_gate_required": not has_full_access, "data": pitch}

    @fastapi_app.get("/api/export/csv")
    async def export_csv(
        category: Optional[str] = None,
        city: Optional[str] = None,
        crm_stage: Optional[str] = None,
        master_key: Optional[str] = None,
        starred: Optional[str] = None,
        x_master_key: Optional[str] = Header(None),
        x_starred: Optional[str] = Header(None)
    ):
        is_starred = (x_starred == "1" or starred in ["1", "true", "True"])
        is_pro = (x_master_key == MASTER_KEY or master_key == MASTER_KEY or is_starred)
        limit = 10000 if is_pro else COMMUNITY_MAX_LEADS_PER_SEARCH
        leads = db.list_leads(category=category, city=city, crm_stage=crm_stage, limit=limit)
        csv_content = export_service.export_csv(leads)
        return Response(
            content=csv_content.encode("utf-8"),
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="geoleads_export.csv"',
                "X-Is-Pro": "1" if is_pro else "0"
            }
        )

    if os.path.exists(STATIC_DIR):
        fastapi_app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

    return fastapi_app

app = create_fastapi_app()

if __name__ == "__main__":
    run_server()
