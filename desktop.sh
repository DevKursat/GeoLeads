#!/usr/bin/env bash
# ============================================================
# GeoLeads Pro - Native Desktop Launcher
# Launches GeoLeads in dedicated native desktop window mode
# ============================================================

set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# Check Python3 availability
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "[!] Python bulunamadı. Lütfen Python 3 kurun."
    exit 1
fi

# Run desktop launcher
exec $PYTHON_CMD "$DIR/desktop.py"
