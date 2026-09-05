"""
Configuration settings for GeoLeads backend.
Loads settings from environment variables or .env file with sensible defaults.
"""
import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_FILE = os.getenv("GEOLEADS_DB_FILE", str(BASE_DIR / "geoleads.db"))

# Security & Master Key
# Loaded strictly from environment GEOLEADS_MASTER_KEY or .master_key file.
def _resolve_master_key() -> str:
    env_key = os.getenv("GEOLEADS_MASTER_KEY")
    if env_key:
        return env_key.strip()

    # Check root .env file
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        try:
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("GEOLEADS_MASTER_KEY=") and not line.startswith("#"):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        return val
        except Exception:
            pass

    # Check persistent .master_key file
    key_file = BASE_DIR / ".master_key"
    if key_file.exists():
        try:
            val = key_file.read_text(encoding="utf-8").strip()
            if val:
                return val
        except Exception:
            pass

    # Generate a cryptographically secure token on first launch
    generated = secrets.token_urlsafe(24)
    try:
        key_file.write_text(generated, encoding="utf-8")
        try:
            os.chmod(str(key_file), 0o600)
        except Exception:
            pass
    except Exception:
        pass
    return generated

MASTER_KEY = _resolve_master_key()

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
GITHUB_REPO_URL = os.getenv("GITHUB_REPO_URL", "https://github.com/DevKursat/GeoLeads")
