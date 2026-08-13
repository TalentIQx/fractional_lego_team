# ai_coach_server.py
import os
import json
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Header, Request
from pydantic import BaseModel
import httpx

app = FastAPI(title="AI Coach Proxy")

# Required environment variables
AI_PROVIDER_URL = os.environ.get("AI_PROVIDER_URL")  # e.g., "https://api.perplexity.ai/v1/..." or OpenAI endpoint
AI_PROVIDER_KEY = os.environ.get("AI_PROVIDER_KEY")  # provider API key
# Optional client API key that Streamlit app will send in a header to authenticate
CLIENT_API_KEY = os.environ.get("CLIENT_API_KEY")    # shared secret between client and server

if not AI_PROVIDER_URL or not AI_PROVIDER_KEY:
    # We allow startup but endpoint will return 500 if not configured
    app.state.provider_configured = False
else:
    app.state.provider_configured = True

class CoachRequest(BaseModel):
    persona: str
    goal: str
    context: dict
    tone: Optional[str] = "Practical"

class CoachResponse(BaseModel):
    advice: str
    steps: List[str] = []

@app.post("/api/coach", response_model=CoachResponse)
async def coach(req: CoachRequest, x_client_key: Optional[str] = Header(None)):
    # Simple API key check (optional)
    if CLIENT_API_KEY:
        if not x_client_key or x_client_key != CLIENT_API_KEY:
            raise HTTPException(status_code=401, detail="Unauthorized client")

    if not app.state.provider_configured:
        raise HTTPException(status_code=500, detail="AI provider not configured on server. Set AI_PROVIDER_URL and AI_PROVIDER_KEY env vars.")

    # Build a concise prompt for the provider
    prompt = (
        f"Persona: {req.persona}\n"
        f"Tone: {req.tone}\n"
        f"Goal: {req.goal}\n"
        f"Context: Revenue {req.context.get('monthly_revenue')}, Runway {req.context.get('runway')}, Gross margin {req.context.get('gross_margin')}\n\n"
        "Provide a short actionable paragraph (advice) and 3 concise, ordered steps the founder can take. Return only plain text."
    )

    headers = {
        "Authorization": f"Bearer {AI_PROVIDER_KEY}",
        "Content-Type": "application/json"
    }

    # Provider payload: adapt to your provider's API schema
    payload = {
        "model": "gpt-4o-mini",  # placeholder; change to provider model if needed
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 400,
        "temperature": 0.6
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(AI_PROVIDER_URL, json=payload, headers=headers)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI provider request failed: {e}")

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"AI provider error: {resp.status_code} {resp.text}")

    data = resp.json()

    # Attempt to extract text from common provider response shapes
    text = ""
    if isinstance(data, dict):
        # OpenAI-like
        try:
            text = data["choices"][0]["message"]["content"]
        except Exception:
            text = data.get("text") or json.dumps(data)
    else:
        text = str(data)

    # Split into advice + steps heuristically
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    advice = lines[0] if lines else "No advice returned."
    steps = []
    # collect up to 5 lines that look like steps (start with numbers or dashes)
    for l in lines[1:8]:
        if l and (l[0].isdigit() or l.startswith("-") or l.lower().startswith("step")):
            steps.append(l.lstrip("-0123456789. ").strip())
        elif len(steps) < 3 and l:
            steps.append(l)
        if len(steps) >= 3:
            break

    return {"advice": advice, "steps": steps}
