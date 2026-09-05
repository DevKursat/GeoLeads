"""
Configuration settings for GeoLeads backend.
Loads settings from environment variables or .env file with sensible defaults.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_FILE = os.getenv("GEOLEADS_DB_FILE", str(BASE_DIR / "geoleads.db"))

# Security & Master Key
# Default master key for local superuser mode if not set in .env
DEFAULT_MASTER_KEY = "geoleads-pro-2026"
MASTER_KEY = os.getenv("GEOLEADS_MASTER_KEY", DEFAULT_MASTER_KEY)

# Quota limits
COMMUNITY_MAX_LEADS_PER_SEARCH = int(os.getenv("COMMUNITY_MAX_LEADS", "25"))
PRO_MAX_LEADS_PER_SEARCH = int(os.getenv("PRO_MAX_LEADS", "500"))

# AI Engine Settings
AI_PROVIDER = os.getenv("GEOLEADS_AI_PROVIDER", "template")  # 'template', 'gemini', 'openai', 'ollama'
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Crawler settings
CRAWLER_TIMEOUT_SECONDS = int(os.getenv("CRAWLER_TIMEOUT", "8"))
CRAWLER_USER_AGENT = os.getenv(
    "CRAWLER_USER_AGENT",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

# GitHub Repo for Star-Gate
GITHUB_REPO_URL = os.getenv("GITHUB_REPO_URL", "https://github.com/geoleads/geoleads")
