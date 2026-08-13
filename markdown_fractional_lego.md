# Lego Manufacturing Command Center

## Files
- `app.py` — Streamlit UI (black Lego theme, onboarding, AI Coach tab, CSV upload, Monte Carlo, PDF export)
- `ai_coach_server.py` — FastAPI backend (secure AI provider proxy)
- `requirements.txt` — dependencies

## Quick start local
1. Create a virtualenv and install deps:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
