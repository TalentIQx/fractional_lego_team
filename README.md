# Lego Manufacturing Command Center — Deploy Guide

## Files
- `app.py` — Streamlit UI (CSV upload, Monte Carlo with shocks, AI Coach client)
- `ai_coach_server.py` — FastAPI backend (secure AI proxy)
- `requirements.txt` — dependencies for both app and backend

## Quick local setup
1. Create virtualenv and install:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
