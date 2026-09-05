"""
Unit and integration tests for GeoLeads API Handler using mock sockets.
Avoids OS sandbox socket permission errors.
"""
import unittest
import json
import io
from app.main import GeoLeadsRequestHandler, check_is_master
from app.core.config import MASTER_KEY
from app.core.database import db
from app.models import Lead, CRMStage


class MockSocket:
    def __init__(self, request_bytes: bytes):
        self.rfile = io.BytesIO(request_bytes)
        self.wfile = io.BytesIO()

    def makefile(self, mode, *args, **kwargs):
        if 'b' in mode:
            if 'r' in mode:
                return self.rfile
            elif 'w' in mode:
                return self.wfile
        return self.rfile

    def sendall(self, data):
        self.wfile.write(data)


def simulate_request(method: str, path: str, headers: dict = None, body: dict = None):
    headers = headers or {}
    body_bytes = b""
    if body is not None:
        body_bytes = json.dumps(body).encode("utf-8")
        headers["Content-Length"] = str(len(body_bytes))
        headers["Content-Type"] = "application/json"

    raw_req = f"{method} {path} HTTP/1.1\r\nHost: localhost\r\n"
    for k, v in headers.items():
        raw_req += f"{k}: {v}\r\n"
    raw_req += "\r\n"

    raw_req_bytes = raw_req.encode("utf-8") + body_bytes
    mock_sock = MockSocket(raw_req_bytes)

    # Instantiate handler with mock socket
    handler = GeoLeadsRequestHandler(mock_sock, ("127.0.0.1", 12345), None)
    output = mock_sock.wfile.getvalue()

    # Split headers and body
    parts = output.split(b"\r\n\r\n", 1)
    header_text = parts[0].decode("utf-8", errors="ignore")
    status_line = header_text.splitlines()[0]
    status_code = int(status_line.split()[1])

    resp_body = parts[1] if len(parts) > 1 else b""
    return status_code, resp_body, header_text


class TestAPIEndpoints(unittest.TestCase):
    def test_check_is_master(self):
        self.assertTrue(check_is_master({"x-master-key": MASTER_KEY}))
        self.assertFalse(check_is_master({"x-master-key": "invalid-key"}))
        self.assertTrue(check_is_master({}, {"master_key": MASTER_KEY}))
        self.assertFalse(check_is_master({}, {"master_key": "wrong"}))

    def test_health_endpoint(self):
        status, body, headers = simulate_request("GET", "/api/system/health")
        self.assertEqual(status, 200)
        data = json.loads(body.decode("utf-8"))
        self.assertEqual(data["status"], "healthy")

    def test_stats_endpoint(self):
        status, body, headers = simulate_request("GET", "/api/stats")
        self.assertEqual(status, 200)
        data = json.loads(body.decode("utf-8"))
        self.assertTrue(data["success"])
        self.assertIn("total_leads", data["data"])

    def test_verify_master_key_invalid(self):
        status, body, headers = simulate_request(
            "POST",
            "/api/auth/verify-master",
            body={"key": "wrong-key"}
        )
        self.assertEqual(status, 200)
        data = json.loads(body.decode("utf-8"))
        self.assertFalse(data["is_valid"])

    def test_verify_master_key_valid(self):
        status, body, headers = simulate_request(
            "POST",
            "/api/auth/verify-master",
            body={"key": MASTER_KEY}
        )
        self.assertEqual(status, 200)
        data = json.loads(body.decode("utf-8"))
        self.assertTrue(data["is_valid"])
        self.assertTrue(data["pro_unlocked"])

    def test_scrape_endpoint(self):
        status, body, headers = simulate_request(
            "POST",
            "/api/scrape",
            body={"query": "Avukat", "city": "Kadıköy", "max_leads": 3, "deep_crawl": False}
        )
        self.assertEqual(status, 200)
        data = json.loads(body.decode("utf-8"))
        self.assertTrue(data["success"])
        self.assertGreaterEqual(data["count"], 1)

    def test_leads_list_and_stage_update(self):
        # Create a lead
        lead = Lead(name="Test Bürosu", city="İstanbul", category="Hukuk")
        saved = db.save_or_update_lead(lead)

        # Update stage
        status, body, headers = simulate_request(
            "POST",
            f"/api/leads/{saved.id}/stage",
            body={"stage": "CONTACTED", "notes": "Email sent"}
        )
        self.assertEqual(status, 200)
        data = json.loads(body.decode("utf-8"))
        self.assertEqual(data["crm_stage"], "CONTACTED")

    def test_export_csv_endpoint(self):
        status, body, headers = simulate_request("GET", "/api/export/csv")
        self.assertEqual(status, 200)
        self.assertIn("text/csv", headers)
        decoded = body.decode("utf-8")
        self.assertIn("İşletme Adı", decoded)


if __name__ == "__main__":
    unittest.main()
