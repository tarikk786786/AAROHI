"""Optional Indic-Speak TTS for AAROHI (Bodhan AI / AI4Bharat).

Preferred girlfriend voice: **Kavya** (Hindi + English, natural Hinglish).

This is NOT a required dependency. The model is gated on Hugging Face (~6.6 GB) and
needs `transformers`, `torch`, `snac`, `soundfile`, plus a Hugging Face token that
has accepted the model terms. Until then Aarohi keeps Edge TTS (Swara).

License: review Bodhan's terms before redistributing a modified model; self-host for
personal/product use is allowed; hosting as a public API for others needs their OK.

Env:
  HF_TOKEN / HUGGING_FACE_HUB_TOKEN - gated download
  INDIC_SPEAK_MODEL - default bodhan-ai/indic-speak-preview-v2
  INDIC_SPEAK_SPEAKER - default Kavya
  INDIC_SPEAK_DIR - optional local snapshot path (skips download)
"""
from __future__ import annotations

import io
import os
import sys
import threading
import wave
from pathlib import Path
from typing import Any, Optional

MODEL_DEFAULT = "bodhan-ai/indic-speak-preview-v2"
SPEAKER_DEFAULT = "Kavya"
SAMPLE_RATE = 24000

_lock = threading.Lock()
_engine = None
_engine_err = ""
_loaded_from = ""


def _token() -> str:
    return (os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN") or "").strip()


def _model_id() -> str:
    return (os.getenv("INDIC_SPEAK_MODEL") or MODEL_DEFAULT).strip()


def _speaker(cfg: Optional[dict] = None) -> str:
    v = ((cfg or {}).get("voice") or {}) if isinstance(cfg, dict) else {}
    return (str(v.get("indic_speak_speaker") or "").strip()
            or os.getenv("INDIC_SPEAK_SPEAKER") or SPEAKER_DEFAULT)


def _local_dir() -> str:
    return (os.getenv("INDIC_SPEAK_DIR") or "").strip()


def deps_ok() -> tuple[bool, str]:
    missing = []
    for mod in ("torch", "transformers", "soundfile", "numpy"):
        try:
            __import__(mod)
        except Exception:
            missing.append(mod)
    try:
        __import__("snac")
    except Exception:
        missing.append("snac")
    if missing:
        return False, "missing packages: " + ", ".join(missing) + (
            " — run scripts/install-aarohi-voice.ps1 (or pip install torch transformers snac soundfile)")
    return True, ""


def available(cfg: Optional[dict] = None) -> bool:
    ok, _ = deps_ok()
    if not ok:
        return False
    if _local_dir() and Path(_local_dir()).is_dir():
        return True
    # Gated model needs a token unless already cached; we treat deps+token OR local dir as ready-to-try.
    return bool(_token()) or _engine is not None


def status(cfg: Optional[dict] = None) -> dict:
    ok, why = deps_ok()
    out = {
        "provider": "indic_speak",
        "label": "Indic-Speak (Kavya)",
        "speaker": _speaker(cfg),
        "model": _model_id(),
        "sample_rate": SAMPLE_RATE,
        "deps_ok": ok,
        "available": False,
        "loaded": _engine is not None,
        "loaded_from": _loaded_from,
        "reason": "",
        "size_hint": "~6.6 GB model weights (gated Hugging Face download)",
        "license_note": "Bodhan AI terms: attribution + ask before hosting as a public API for others",
        "alternatives": ["indic_f5", "hinglish_tts", "edge:hi-IN-SwaraNeural"],
    }
    if not ok:
        out["reason"] = why
        return out
    if _engine is not None:
        out["available"] = True
        out["reason"] = "loaded"
        return out
    if _local_dir():
        out["available"] = True
        out["reason"] = "local_dir"
        return out
    if _token():
        out["available"] = True
        out["reason"] = "token_ready"
        return out
    out["reason"] = "set HF_TOKEN after accepting the model terms on Hugging Face, or set INDIC_SPEAK_DIR"
    return out


def _resolve_repo() -> str:
    local = _local_dir()
    if local:
        return local
    from huggingface_hub import snapshot_download
    return snapshot_download(_model_id(), token=_token() or None)


def _load_engine():
    global _engine, _engine_err, _loaded_from
    with _lock:
        if _engine is not None:
            return _engine
        ok, why = deps_ok()
        if not ok:
            _engine_err = why
            raise RuntimeError(why)
        try:
            root = _resolve_repo()
            if root not in sys.path:
                sys.path.insert(0, root)
            from inference import TTS  # type: ignore  # shipped inside the HF snapshot
            _engine = TTS(root)
            _loaded_from = root
            _engine_err = ""
            return _engine
        except Exception as e:
            _engine_err = f"{type(e).__name__}: {e}"
            raise


def _float_to_wav_bytes(wav, rate: int = SAMPLE_RATE) -> bytes:
    import numpy as np
    arr = np.asarray(wav, dtype=np.float32).reshape(-1)
    arr = np.clip(arr, -1.0, 1.0)
    pcm = (arr * 32767.0).astype("<i2")
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm.tobytes())
    return buf.getvalue()


def synth_sync(text: str, cfg: Optional[dict] = None) -> bytes:
    """Return WAV bytes (PCM 16-bit mono @ 24 kHz)."""
    text = (text or "").strip()
    if not text:
        raise ValueError("empty text")
    eng = _load_engine()
    speaker = _speaker(cfg)
    style = str(((cfg or {}).get("voice") or {}).get("indic_speak_style") or "").strip() or None
    kwargs: dict[str, Any] = {"speaker": speaker}
    if style:
        kwargs["style"] = style
    wav = eng(text, **kwargs)
    return _float_to_wav_bytes(wav, SAMPLE_RATE)


async def synth(text: str, cfg: Optional[dict] = None) -> bytes:
    import asyncio
    return await asyncio.to_thread(synth_sync, text, cfg)
