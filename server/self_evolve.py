"""AAROHI Self-Evolve facade (phase 1).

Does NOT replace learn.py / improvement_* — those already own self-learning,
skill candidates, experiments, canaries, sandboxes and owner approval.

This module:
  - records structured *experience* events (success/fail/correction/tool error)
  - exposes aggregated status for agents + dashboard
  - accepts *research proposals* (never clones/installs)
  - never auto-deploys skills or code

See docs/en/autonomous-self-evolving.md and system/self-evolve-registry.json.
"""
from __future__ import annotations

import json
import sqlite3
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "self-evolve-v1"
_LOCK = threading.RLock()

EVENT_TYPES = (
    "task_success",
    "task_failure",
    "user_correction",
    "repeated_request",
    "api_execution",
    "tool_error",
    "perf_bottleneck",
    "agent_collab",
    "human_approved",
    "research_note",
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _dir(brain: Path) -> Path:
    d = Path(brain) / ".javis" / "self_evolve"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _db(brain: Path) -> Path:
    return _dir(brain) / "experience.sqlite3"


def _conn(brain: Path) -> sqlite3.Connection:
    c = sqlite3.connect(str(_db(brain)), check_same_thread=False)
    c.row_factory = sqlite3.Row
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS experiences (
            id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            summary TEXT NOT NULL,
            detail TEXT,
            skill_slug TEXT,
            tool_name TEXT,
            success INTEGER,
            tokens INTEGER,
            latency_ms INTEGER,
            cost_usd REAL,
            tags TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS research_proposals (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            repo_url TEXT,
            rationale TEXT,
            license_note TEXT,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            decided_at TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS metrics_daily (
            day TEXT NOT NULL,
            key TEXT NOT NULL,
            value REAL NOT NULL,
            PRIMARY KEY (day, key)
        )
        """
    )
    c.execute(
        "CREATE INDEX IF NOT EXISTS idx_exp_type ON experiences(event_type, created_at)"
    )
    return c


def record_experience(
    brain: str | Path,
    *,
    event_type: str,
    summary: str,
    detail: str = "",
    skill_slug: str = "",
    tool_name: str = "",
    success: bool | None = None,
    tokens: int = 0,
    latency_ms: int = 0,
    cost_usd: float = 0.0,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    et = str(event_type or "").strip()
    if et not in EVENT_TYPES:
        return {"ok": False, "error": f"event_type must be one of {EVENT_TYPES}"}
    summary = (summary or "").strip()
    if not summary:
        return {"ok": False, "error": "empty summary"}
    brain = Path(brain)
    eid = uuid.uuid4().hex[:16]
    now = _now()
    with _LOCK:
        c = _conn(brain)
        try:
            c.execute(
                """
                INSERT INTO experiences(
                    id, event_type, summary, detail, skill_slug, tool_name,
                    success, tokens, latency_ms, cost_usd, tags, created_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    eid,
                    et,
                    summary[:2000],
                    (detail or "")[:8000],
                    skill_slug or "",
                    tool_name or "",
                    None if success is None else (1 if success else 0),
                    int(tokens or 0),
                    int(latency_ms or 0),
                    float(cost_usd or 0),
                    json.dumps(tags or [], ensure_ascii=False),
                    now,
                ),
            )
            day = now[:10]
            # Rolling counters
            for key, inc in (
                ("events_total", 1.0),
                (f"events_{et}", 1.0),
                ("tokens_total", float(tokens or 0)),
                ("cost_usd_total", float(cost_usd or 0)),
            ):
                if inc == 0 and key != "events_total":
                    continue
                c.execute(
                    """
                    INSERT INTO metrics_daily(day, key, value) VALUES(?,?,?)
                    ON CONFLICT(day, key) DO UPDATE SET value = value + excluded.value
                    """,
                    (day, key, inc),
                )
            if success is True:
                c.execute(
                    """
                    INSERT INTO metrics_daily(day, key, value) VALUES(?,?,1)
                    ON CONFLICT(day, key) DO UPDATE SET value = value + 1
                    """,
                    (day, "task_success"),
                )
            elif success is False:
                c.execute(
                    """
                    INSERT INTO metrics_daily(day, key, value) VALUES(?,?,1)
                    ON CONFLICT(day, key) DO UPDATE SET value = value + 1
                    """,
                    (day, "task_failure"),
                )
            c.commit()
        finally:
            c.close()
    return {"ok": True, "id": eid, "event_type": et, "created_at": now}


def list_experiences(brain: str | Path, *, limit: int = 50, event_type: str = "") -> dict[str, Any]:
    brain = Path(brain)
    limit = max(1, min(int(limit or 50), 200))
    with _LOCK:
        c = _conn(brain)
        try:
            if event_type:
                rows = c.execute(
                    "SELECT * FROM experiences WHERE event_type=? ORDER BY created_at DESC LIMIT ?",
                    (event_type, limit),
                ).fetchall()
            else:
                rows = c.execute(
                    "SELECT * FROM experiences ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        finally:
            c.close()
    return {"ok": True, "items": [dict(r) for r in rows]}


def propose_research(
    brain: str | Path,
    *,
    title: str,
    repo_url: str = "",
    rationale: str = "",
    license_note: str = "",
) -> dict[str, Any]:
    """Queue a research proposal — never clones or installs."""
    title = (title or "").strip()
    if not title:
        return {"ok": False, "error": "empty title"}
    brain = Path(brain)
    rid = uuid.uuid4().hex[:12]
    now = _now()
    with _LOCK:
        c = _conn(brain)
        try:
            c.execute(
                """
                INSERT INTO research_proposals(
                    id, title, repo_url, rationale, license_note, status, created_at
                ) VALUES (?,?,?,?,?,'pending',?)
                """,
                (
                    rid,
                    title[:200],
                    (repo_url or "")[:500],
                    (rationale or "")[:4000],
                    (license_note or "")[:500],
                    now,
                ),
            )
            c.commit()
        finally:
            c.close()
    return {
        "ok": True,
        "id": rid,
        "status": "pending",
        "note": "Proposal stored for owner review. Never clones or installs automatically.",
    }


def decide_research(brain: str | Path, proposal_id: str, *, approve: bool) -> dict[str, Any]:
    brain = Path(brain)
    status = "approved_review" if approve else "rejected"
    with _LOCK:
        c = _conn(brain)
        try:
            row = c.execute(
                "SELECT id FROM research_proposals WHERE id=?", (proposal_id,)
            ).fetchone()
            if not row:
                return {"ok": False, "error": "not found"}
            c.execute(
                "UPDATE research_proposals SET status=?, decided_at=? WHERE id=?",
                (status, _now(), proposal_id),
            )
            c.commit()
        finally:
            c.close()
    return {
        "ok": True,
        "id": proposal_id,
        "status": status,
        "note": (
            "Approved for human-led evaluation only — still no auto-install."
            if approve
            else "Rejected."
        ),
    }


def metrics(brain: str | Path, *, days: int = 14) -> dict[str, Any]:
    brain = Path(brain)
    days = max(1, min(int(days or 14), 90))
    with _LOCK:
        c = _conn(brain)
        try:
            rows = c.execute(
                "SELECT day, key, value FROM metrics_daily ORDER BY day DESC"
            ).fetchall()
            pending = c.execute(
                "SELECT COUNT(*) n FROM research_proposals WHERE status='pending'"
            ).fetchone()["n"]
            exp_n = c.execute("SELECT COUNT(*) n FROM experiences").fetchone()["n"]
        finally:
            c.close()
    by_day: dict[str, dict[str, float]] = {}
    for r in rows:
        by_day.setdefault(r["day"], {})[r["key"]] = float(r["value"])
    # keep last N days
    ordered = sorted(by_day.keys(), reverse=True)[:days]
    series = {d: by_day[d] for d in ordered}
    # success rate
    succ = sum(by_day[d].get("task_success", 0) for d in ordered)
    fail = sum(by_day[d].get("task_failure", 0) for d in ordered)
    rate = (succ / (succ + fail)) if (succ + fail) else None
    return {
        "ok": True,
        "schema": SCHEMA,
        "experience_count": exp_n,
        "research_pending": pending,
        "task_success_rate": rate,
        "series": series,
        "authority": {
            "skill_deploy": "improvement candidates + owner authorize (never this module)",
            "self_learning": "Self-learning page / learn.py",
            "knowledge": "knowledge_intel.py",
        },
    }


def status(brain: str | Path) -> dict[str, Any]:
    """Aggregate pointer status for the Self-Improvement Center / agents."""
    brain = Path(brain)
    m = metrics(brain)
    learn_hint = {
        "page": "Self-learning (Brain group)",
        "writes": "Python writer only after JSON extract; git undo when available",
        "skills_path": "skills/<slug>/SKILL.md",
    }
    improvement_hint = {
        "ui": "improvement-candidates / experiments panels",
        "rule": "Candidate must beat baseline on sealed qualification; owner approve",
        "activation_auto": False,
    }
    return {
        "ok": True,
        "brain": str(brain),
        "metrics": m,
        "learn": learn_hint,
        "improvement": improvement_hint,
        "loop": [
            "OBSERVE",
            "ANALYZE",
            "EXTRACT",
            "LEARN",
            "GENERATE",
            "TEST",
            "COMPARE",
            "APPROVE",
            "DEPLOY",
            "MONITOR",
        ],
        "vercel_note": "Long-running self-improve workers need local/Docker — not Vercel serverless.",
    }


OPS = (
    "status",
    "record",
    "list",
    "metrics",
    "propose_research",
    "decide_research",
)


def run(args: dict, vault_root: str) -> str:
    op = str((args or {}).get("op") or "").strip()
    if not vault_root:
        return json.dumps({"ok": False, "error": "no brain"}, ensure_ascii=False)
    if op not in OPS:
        return json.dumps({"ok": False, "error": f"op must be one of {OPS}"}, ensure_ascii=False)
    brain = Path(vault_root)
    try:
        if op == "status":
            out = status(brain)
        elif op == "record":
            out = record_experience(
                brain,
                event_type=str(args.get("event_type") or ""),
                summary=str(args.get("summary") or ""),
                detail=str(args.get("detail") or ""),
                skill_slug=str(args.get("skill_slug") or ""),
                tool_name=str(args.get("tool_name") or ""),
                success=args.get("success") if "success" in args else None,
                tokens=int(args.get("tokens") or 0),
                latency_ms=int(args.get("latency_ms") or 0),
                cost_usd=float(args.get("cost_usd") or 0),
                tags=list(args.get("tags") or []) if isinstance(args.get("tags"), list) else [],
            )
        elif op == "list":
            out = list_experiences(
                brain,
                limit=int(args.get("limit") or 50),
                event_type=str(args.get("event_type") or ""),
            )
        elif op == "metrics":
            out = metrics(brain, days=int(args.get("days") or 14))
        elif op == "propose_research":
            out = propose_research(
                brain,
                title=str(args.get("title") or ""),
                repo_url=str(args.get("repo_url") or ""),
                rationale=str(args.get("rationale") or ""),
                license_note=str(args.get("license_note") or ""),
            )
        else:
            out = decide_research(
                brain,
                str(args.get("id") or ""),
                approve=bool(args.get("approve")),
            )
    except Exception as e:  # noqa: BLE001
        out = {"ok": False, "error": f"{type(e).__name__}: {e}"}
    return json.dumps(out, ensure_ascii=False, indent=2)
