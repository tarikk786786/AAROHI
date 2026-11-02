"""One-shot AAROHI Mark-style voice pin (no Mark-LVI source copied)."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))

import config as cfgmod  # noqa: E402


def patch_voice_js() -> None:
    p = ROOT / "dashboard" / "voice.js"
    t = p.read_text(encoding="utf-8")
    if 'ttsRate = opts.ttsRate || "-8%"' in t:
        print("voice.js already -8%")
        return
    t2 = t.replace(
        'this.ttsRate = opts.ttsRate || "-5%";',
        'this.ttsRate = opts.ttsRate || "-8%"; // Mark-style soft pace',
        1,
    )
    if t2 == t:
        raise SystemExit("voice.js: could not patch ttsRate")
    p.write_text(t2, encoding="utf-8")
    print("voice.js patched to -8%")


def pin_settings() -> None:
    cfg = cfgmod.read_settings()
    v = cfg.setdefault("voice", {})
    v["edge_voice"] = "hi-IN-SwaraNeural"
    v["tts_provider"] = "edge"
    v["tts_rate"] = "-8%"
    v["prefer_indic_speak"] = False
    v["mode"] = "fast"
    v["call_engine"] = "basic"
    v["brain_provider"] = "groq"
    bm = v.setdefault("brain_models", {})
    if not isinstance(bm, dict):
        bm = {}
        v["brain_models"] = bm
    bm["groq"] = bm.get("groq") or "llama-3.3-70b-versatile"
    if (cfg.get("model") or {}).get("groq_api_key"):
        v["stt_provider"] = "groq"
        v["ear"] = "auto"
    cfg.setdefault("locale", {})["reply_lang"] = "hi"
    cfgmod.write_settings(cfg)
    print("settings pinned", v.get("brain_provider"), v.get("tts_rate"), v.get("edge_voice"))


def mirror() -> None:
    for name in ("voice.js", "app.js"):
        shutil.copy2(ROOT / "dashboard" / name, ROOT / "server" / "dashboard" / name)
    print("mirrored dashboard assets")


if __name__ == "__main__":
    patch_voice_js()
    pin_settings()
    mirror()
