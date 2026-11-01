"""Vercel entrypoint for AAROHI / Javis OS."""
import os
import sys
from pathlib import Path

# When running inside Vercel Serverless Function, disk is read-only except /tmp
if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    os.environ.setdefault("JAVIS_STATE_DIR", "/tmp/javis_state")
    os.environ.setdefault("BRAINS_DIR", "/tmp/brains")
    os.environ.setdefault("HOME", "/tmp")
    os.environ.setdefault("JAVIS_ALLOWED_HOSTS", "localhost,127.0.0.1,aarohi-theta.vercel.app,*.vercel.app")
    Path("/tmp/javis_state").mkdir(parents=True, exist_ok=True)
    Path("/tmp/brains").mkdir(parents=True, exist_ok=True)

# Add server directory to sys.path so modules inside server can import each other
root_dir = Path(__file__).resolve().parent
server_dir = root_dir / "server"
if str(server_dir) not in sys.path:
    sys.path.insert(0, str(server_dir))
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from server.main import app  # noqa: E402
