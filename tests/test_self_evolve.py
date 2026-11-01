"""Self-evolve experience facade — no auto-deploy."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))

import self_evolve  # noqa: E402


def test_record_and_metrics():
    with tempfile.TemporaryDirectory() as td:
        brain = Path(td)
        r = self_evolve.record_experience(
            brain,
            event_type="task_success",
            summary="Fixed deploy env",
            success=True,
            tokens=120,
        )
        assert r["ok"] and r["id"]
        listed = self_evolve.list_experiences(brain, limit=10)
        assert listed["ok"] and len(listed["items"]) == 1
        m = self_evolve.metrics(brain)
        assert m["ok"] and m["experience_count"] == 1
        assert m["task_success_rate"] == 1.0


def test_research_never_installs():
    with tempfile.TemporaryDirectory() as td:
        brain = Path(td)
        p = self_evolve.propose_research(
            brain,
            title="Evaluate DeepEval for CI",
            repo_url="https://github.com/confident-ai/deepeval",
            rationale="Offline eval beside qualification cases",
        )
        assert p["ok"]
        assert "never" in p.get("note", "").lower()
        d = self_evolve.decide_research(brain, p["id"], approve=True)
        assert d["ok"] and d["status"] == "approved_review"
        st = self_evolve.status(brain)
        assert st["ok"] and "APPROVE" in st["loop"]
        assert st["improvement"]["activation_auto"] is False


def test_rejects_bad_event_type():
    with tempfile.TemporaryDirectory() as td:
        r = self_evolve.record_experience(Path(td), event_type="nope", summary="x")
        assert not r["ok"]
