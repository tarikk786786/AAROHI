"""Optional Shruti STT ear for AAROHI (Udgam Labs).

Offline Hindi / English / Hinglish speech-to-text from one ~29.5 MB file
(`udgamlabs/Shruti` + `cactus-needle`). Apache-2.0.

Not a required dependency. When packages + weights are present, voice_ear can
prefer Shruti for local Hinglish without a cloud key.

Env:
  SHRUTI_CACT - absolute path to shruti.cact (skips Hub download)
  NEEDLE_TELEMETRY=0 - recommended; install script sets this
"""
from __future__ import annotations

import os
import tempfile
import threading
from pathlib import Path
from typing import Optional

MODEL_REPO = "udgamlabs/Shruti"
MODEL_FILE = "shruti.cact"

_lock = threading.Lock()
_model = None
_model_path = ""
_err = ""


def deps_ok() -> tuple[bool, str]:
    try:
        import needle  # noqa: F401
        from huggingface_hub import hf_hub_download  # noqa: F401
    except Exception:
        return False, "missing cactus-needle (pip install cactus-needle)"
    return True, ""


def _cact_path() -> str:
    forced = (os.getenv("SHRUTI_CACT") or "").strip()
    if forced and Path(forced).is_file():
        return forced
    from huggingface_hub import hf_hub_download
    return hf_hub_download(MODEL_REPO, MODEL_FILE)


def available() -> bool:
    ok, _ = deps_ok()
    return ok


def status() -> dict:
    ok, why = deps_ok()
    return {
        "provider": "shruti",
        "label": "Shruti (offline Hinglish STT)",
        "available": ok,
        "loaded": _model is not None,
        "model_path": _model_path,
        "size_hint": "29.5 MB quantized (.cact)",
        "license": "Apache-2.0",
        "reason": "ready" if ok else why,
        "repo": MODEL_REPO,
    }


def _load():
    global _model, _model_path, _err
    with _lock:
        if _model is not None:
            return _model
        ok, why = deps_ok()
        if not ok:
            _err = why
            raise RuntimeError(why)
        os.environ.setdefault("NEEDLE_TELEMETRY", "0")
        from needle import Whistle
        path = _cact_path()
        _model = Whistle(path)
        _model_path = path
        _err = ""
        return _model


def _write_temp_audio(data: bytes, filename: str) -> Path:
    suffix = Path(filename or "voice.webm").suffix or ".webm"
    if suffix.lower() not in (".wav", ".webm", ".ogg", ".mp3", ".m4a", ".flac"):
        suffix = ".webm"
    fd, name = tempfile.mkstemp(prefix="aarohi-shruti-", suffix=suffix)
    os.close(fd)
    path = Path(name)
    path.write_bytes(data)
    return path


def _maybe_to_wav(src: Path) -> Path:
    """Shruti wants audio the needle engine can read; convert via ffmpeg when not wav."""
    if src.suffix.lower() == ".wav":
        return src
    import shutil
    import subprocess
    if not shutil.which("ffmpeg"):
        return src  # hope needle accepts the container; else caller sees the error
    out = src.with_suffix(".wav")
    cmd = ["ffmpeg", "-y", "-i", str(src), "-ac", "1", "-ar", "16000", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not out.is_file():
        return src
    return out


def transcribe_sync(data: bytes, filename: str = "voice.webm",
                    language: Optional[str] = None,
                    keywords: Optional[list] = None) -> dict:
    """Same shape as stt.groq_nghe results: {ok, text, model, ly_do?}."""
    if not data:
        return {"ok": False, "text": "", "ly_do": "empty", "model": "shruti"}
    path = None
    wav = None
    try:
        model = _load()
        path = _write_temp_audio(data, filename)
        wav = _maybe_to_wav(path)
        kw = {"keywords": keywords} if keywords else {}
        if language in ("hi", "en"):
            kw["language"] = language
        out = model.transcribe(str(wav), **kw)
        if isinstance(out, dict):
            text = str(out.get("text") or "").strip()
        else:
            text = str(out or "").strip()
        if not text:
            return {"ok": False, "text": "", "ly_do": "empty_transcript", "model": "shruti"}
        return {"ok": True, "text": text, "model": "shruti"}
    except Exception as e:
        return {"ok": False, "text": "", "ly_do": f"shruti_error:{type(e).__name__}",
                "model": "shruti", "noi_voi_javis": str(e)[:200]}
    finally:
        for p in (path, wav):
            if p and p.exists():
                try:
                    if path and wav and p == wav and wav != path:
                        p.unlink(missing_ok=True)
                    elif p == path:
                        p.unlink(missing_ok=True)
                except Exception:
                    pass


async def transcribe(data: bytes, filename: str = "voice.webm",
                     language: Optional[str] = None,
                     keywords: Optional[list] = None) -> dict:
    import asyncio
    return await asyncio.to_thread(transcribe_sync, data, filename, language, keywords)
