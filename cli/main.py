"""FastAPI service wrapper for Javis CLI on Vercel."""
import os
import sys
from pathlib import Path

# Add cli directory to sys.path so javis_cli can be imported
cli_dir = Path(__file__).resolve().parent
if str(cli_dir) not in sys.path:
    sys.path.insert(0, str(cli_dir))

from fastapi import FastAPI, HTTPException
from javis_cli.client import Client, LoiJavis
from javis_cli.config import ho_so

app = FastAPI(title="AAROHI / Javis CLI Internal Service")


@app.get("/health")
def health():
    cfg = ho_so()
    target_url = cfg.get("url") or os.getenv("JAVIS_URL", "")
    return {
        "status": "ok",
        "service": "cli",
        "bound_app_url": target_url
    }


@app.get("/status")
def status():
    cfg = ho_so()
    url = cfg.get("url") or os.getenv("JAVIS_URL")
    token = cfg.get("token") or os.getenv("JAVIS_TOKEN", "")
    if not url:
        raise HTTPException(status_code=500, detail="JAVIS_URL service binding is not set")
    try:
        client = Client(url, token)
        return client.get("/health")
    except LoiJavis as e:
        raise HTTPException(status_code=502, detail=str(e))
