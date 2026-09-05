#!/usr/bin/env bash
# ============================================================
# GeoLeads Pro - Quick Launch Script
# ============================================================

set -e

echo "========================================================"
echo "   GeoLeads Pro - B2B Müşteri Bulma & Satış Motoru    "
echo "========================================================"

PORT=${PORT:-8000}

# Check Python3 availability
if ! command -v python3 &> /dev/null; then
    echo "[!] Python 3 bulunamadı. Lütfen Python 3 kurun."
    exit 1
fi

echo "[*] Veritabanı ve servisler hazırlanıyor..."

cd "$(dirname "$0")/backend"

echo "[✓] GeoLeads hazır!"
echo "[*] Web arayüzü başlatılıyor: http://localhost:$PORT"
echo "========================================================"
echo " Master Admin Key: geoleads-pro-2026"
echo "========================================================"

python3 server.py "$PORT"
