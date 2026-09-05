#!/usr/bin/env python3
"""
GeoLeads Server Entry Point
Usage: python3 server.py [--port 8000]
"""
import sys
import os

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import run_server, HAS_FASTAPI

if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])

    if HAS_FASTAPI:
        try:
            import uvicorn
            print(f"🚀 Starting GeoLeads with FastAPI & Uvicorn on http://0.0.0.0:{port}")
            uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info")
            sys.exit(0)
        except Exception:
            pass

    run_server(port=port)
