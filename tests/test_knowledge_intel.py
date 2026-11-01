"""Knowledge intel — dedupe, search, forget."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))

import knowledge_intel as ki  # noqa: E402


def test_ingest_dedupe_and_search():
    with tempfile.TemporaryDirectory() as td:
        brain = Path(td)
        a = ki.ingest(brain, text="Aarohi prefers Hinglish replies.", title="language preference")
        assert a["ok"] and a["status"] == "created"
        b = ki.ingest(brain, text="Aarohi prefers Hinglish replies.", title="language preference")
        assert b["ok"] and b["status"] == "duplicate"
        s = ki.search(brain, "Hinglish", include_memory_index=False)
        assert s["ok"] and len(s["hits"]) >= 1
        st = ki.stats(brain)
        assert st["records"] == 1
        pkt = ki.answer_packet(brain, "Hinglish", limit=3)
        assert pkt["ok"] and not pkt["insufficient"]


def test_forget_soft():
    with tempfile.TemporaryDirectory() as td:
        brain = Path(td)
        a = ki.ingest(brain, text="Temporary fact about deploy.", title="deploy")
        f = ki.forget(brain, a["id"], hard=False)
        assert f["ok"]
        g = ki.get_record(brain, a["id"])
        assert not g["ok"]
