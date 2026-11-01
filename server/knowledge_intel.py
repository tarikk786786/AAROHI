"""AAROHI Universal Knowledge Intelligence Engine (phase 1).

Markdown vault remains the source of truth (sources/ → wiki/ → memory/).
This module adds provenance, dedup, versioning metadata, hybrid retrieval
wrappers, conflict/outdated hints, and a stable REST/MCP contract — without
installing RAGFlow / LlamaIndex / Mem0 as a second orchestration stack.

Optional later: pgvector / Qdrant / Docling workers as sidecars (see
docs/en/universal-knowledge-intelligence.md).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import threading
import time
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "knowledge-intel-v1"
_WORD_RE = re.compile(r"[^\W_]{2,}", re.UNICODE)
_LOCK = threading.RLock()


def _sha(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8", errors="replace")).hexdigest()


def _norm(value: str) -> str:
    raw = str(value or "").replace("đ", "d").replace("Đ", "D")
    raw = unicodedata.normalize("NFKD", raw.casefold())
    return " ".join(_WORD_RE.findall("".join(c for c in raw if not unicodedata.combining(c))))


def _terms(value: str) -> list[str]:
    stop = {
        "cua", "cho", "voi", "nhung", "mot", "nay", "kia", "the", "anh", "toi",
        "co", "khong", "la", "gi", "and", "for", "that", "what", "the", "with",
        "from", "this", "have", "has", "are", "was", "were", "jaan", "babe",
    }
    return [x for x in dict.fromkeys(_norm(value).split()) if x not in stop and len(x) > 1]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def knowledge_dir(brain: Path) -> Path:
    d = Path(brain) / ".javis" / "knowledge"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _db_path(brain: Path) -> Path:
    return knowledge_dir(brain) / "intel.sqlite3"


def _connect(brain: Path) -> sqlite3.Connection:
    path = _db_path(brain)
    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS records (
            id TEXT PRIMARY KEY,
            kind TEXT NOT NULL,
            title TEXT,
            body TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            source_uri TEXT,
            source_type TEXT,
            provenance TEXT,
            tags TEXT,
            confidence REAL DEFAULT 0.5,
            verified INTEGER DEFAULT 0,
            outdated INTEGER DEFAULT 0,
            conflict_of TEXT,
            version INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            relative_path TEXT,
            deleted INTEGER DEFAULT 0
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_kh_hash ON records(content_hash)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_kh_kind ON records(kind, deleted)"
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )
    conn.execute(
        "INSERT OR IGNORE INTO meta(key, value) VALUES('schema', ?)",
        (SCHEMA_VERSION,),
    )
    return conn


@dataclass
class Hit:
    id: str
    title: str
    snippet: str
    score: float
    source_uri: str
    relative_path: str
    confidence: float
    verified: bool
    outdated: bool
    kind: str


def _score_text(query_terms: list[str], title: str, body: str) -> float:
    if not query_terms:
        return 0.0
    blob = _norm(f"{title}\n{body}")
    hit = sum(1 for t in query_terms if t in blob)
    title_n = _norm(title)
    title_hit = sum(1 for t in query_terms if t in title_n)
    return (hit / max(1, len(query_terms))) * 0.7 + (title_hit / max(1, len(query_terms))) * 0.3


def ingest(
    brain: str | Path,
    *,
    text: str,
    title: str = "",
    kind: str = "fact",
    source_uri: str = "",
    source_type: str = "chat",
    tags: list[str] | None = None,
    confidence: float = 0.6,
    verified: bool = False,
    write_markdown: bool = True,
) -> dict[str, Any]:
    """Ingest knowledge: dedupe by content hash, version on change, optional wiki note."""
    brain = Path(brain)
    body = (text or "").strip()
    if not body:
        return {"ok": False, "error": "empty text"}
    title = (title or body.split("\n", 1)[0][:80]).strip()
    ch = _sha(body)
    now = _now_iso()
    with _LOCK:
        conn = _connect(brain)
        try:
            row = conn.execute(
                "SELECT id, version, body FROM records WHERE content_hash=? AND deleted=0",
                (ch,),
            ).fetchone()
            if row:
                return {
                    "ok": True,
                    "status": "duplicate",
                    "id": row["id"],
                    "version": row["version"],
                    "message": "already known (same content hash)",
                }
            # Soft conflict: same title, different body
            conflict = conn.execute(
                "SELECT id, body, version FROM records WHERE title=? AND deleted=0 AND content_hash!=? LIMIT 1",
                (title, ch),
            ).fetchone()
            rid = _sha(f"{now}:{title}:{ch}")[:24]
            rel = ""
            if write_markdown:
                rel = _write_wiki_note(brain, rid, title, body, source_uri, kind, tags or [])
            conn.execute(
                """
                INSERT INTO records(
                    id, kind, title, body, content_hash, source_uri, source_type,
                    provenance, tags, confidence, verified, outdated, conflict_of,
                    version, created_at, updated_at, relative_path, deleted
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,0)
                """,
                (
                    rid,
                    kind,
                    title,
                    body,
                    ch,
                    source_uri or "",
                    source_type,
                    json.dumps({"ingested_at": now, "source_uri": source_uri}, ensure_ascii=False),
                    json.dumps(tags or [], ensure_ascii=False),
                    float(confidence),
                    1 if verified else 0,
                    0,
                    conflict["id"] if conflict else None,
                    1,
                    now,
                    now,
                    rel,
                ),
            )
            if conflict:
                conn.execute(
                    "UPDATE records SET outdated=1, updated_at=? WHERE id=?",
                    (now, conflict["id"]),
                )
            conn.commit()
            out = {
                "ok": True,
                "status": "created",
                "id": rid,
                "version": 1,
                "relative_path": rel,
                "content_hash": ch,
            }
            if conflict:
                out["conflict_of"] = conflict["id"]
                out["warning"] = "possible contradiction with an existing record of the same title"
            return out
        finally:
            conn.close()


def _write_wiki_note(
    brain: Path, rid: str, title: str, body: str, source_uri: str, kind: str, tags: list[str]
) -> str:
    folder = Path(brain) / "wiki" / "knowledge"
    folder.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^\w\-]+", "-", title.casefold()).strip("-")[:48] or "note"
    name = f"{safe}-{rid[:8]}.md"
    path = folder / name
    fm = [
        "---",
        f"id: {rid}",
        f"title: {json.dumps(title, ensure_ascii=False)}",
        f"kind: {kind}",
        f"source: {json.dumps(source_uri or '', ensure_ascii=False)}",
        f"tags: {json.dumps(tags, ensure_ascii=False)}",
        f"updated: {_now_iso()}",
        "---",
        "",
        f"# {title}",
        "",
        body.strip(),
        "",
    ]
    if source_uri:
        fm.extend(["", f"_Source: {source_uri}_", ""])
    path.write_text("\n".join(fm), encoding="utf-8")
    return f"wiki/knowledge/{name}"


def search(
    brain: str | Path,
    query: str,
    *,
    limit: int = 8,
    include_memory_index: bool = True,
) -> dict[str, Any]:
    """Hybrid retrieval: knowledge sqlite + optional memory_index cascade."""
    brain = Path(brain)
    q = (query or "").strip()
    if not q:
        return {"ok": False, "error": "empty query", "hits": []}
    terms = _terms(q)
    hits: list[Hit] = []
    with _LOCK:
        conn = _connect(brain)
        try:
            rows = conn.execute(
                "SELECT * FROM records WHERE deleted=0 ORDER BY updated_at DESC LIMIT 500"
            ).fetchall()
        finally:
            conn.close()
    for row in rows:
        score = _score_text(terms, row["title"] or "", row["body"] or "")
        if score <= 0:
            continue
        if row["outdated"]:
            score *= 0.55
        if row["verified"]:
            score *= 1.15
        snippet = (row["body"] or "")[:280]
        hits.append(
            Hit(
                id=row["id"],
                title=row["title"] or "",
                snippet=snippet,
                score=round(score, 4),
                source_uri=row["source_uri"] or "",
                relative_path=row["relative_path"] or "",
                confidence=float(row["confidence"] or 0),
                verified=bool(row["verified"]),
                outdated=bool(row["outdated"]),
                kind=row["kind"] or "fact",
            )
        )
    hits.sort(key=lambda h: (-h.score, -h.confidence, h.title))
    hits = hits[: max(1, min(limit, 30))]

    memory_hits: list[dict] = []
    if include_memory_index:
        try:
            from memory_index import MemoryIndex

            ret = MemoryIndex().retrieve(Path(brain), q, limit=limit)
            for rec in getattr(ret, "records", ()) or []:
                if not isinstance(rec, dict):
                    continue
                memory_hits.append(
                    {
                        "path": rec.get("relative") or rec.get("path") or rec.get("source_path") or "",
                        "excerpt": (rec.get("excerpt") or rec.get("detail") or rec.get("text") or "")[:280],
                        "score": rec.get("retrieval_score") or rec.get("score"),
                        "layer": "memory_index",
                    }
                )
        except Exception as e:  # noqa: BLE001
            memory_hits = [{"error": f"{type(e).__name__}: {e}"}]

    return {
        "ok": True,
        "query": q,
        "hits": [h.__dict__ for h in hits],
        "memory_index": memory_hits,
        "guidance": (
            "Cite relative_path / source_uri. Treat outdated=true as historical. "
            "If hits are empty, admit insufficient knowledge."
        ),
    }


def get_record(brain: str | Path, record_id: str) -> dict[str, Any]:
    brain = Path(brain)
    with _LOCK:
        conn = _connect(brain)
        try:
            row = conn.execute(
                "SELECT * FROM records WHERE id=? AND deleted=0", (record_id,)
            ).fetchone()
        finally:
            conn.close()
    if not row:
        return {"ok": False, "error": "not found"}
    return {"ok": True, "record": dict(row)}


def forget(brain: str | Path, record_id: str, *, hard: bool = False) -> dict[str, Any]:
    """User-controlled deletion. Soft-delete by default; hard removes row + optional md."""
    brain = Path(brain)
    with _LOCK:
        conn = _connect(brain)
        try:
            row = conn.execute("SELECT * FROM records WHERE id=?", (record_id,)).fetchone()
            if not row:
                return {"ok": False, "error": "not found"}
            rel = row["relative_path"] or ""
            if hard:
                conn.execute("DELETE FROM records WHERE id=?", (record_id,))
            else:
                conn.execute(
                    "UPDATE records SET deleted=1, updated_at=? WHERE id=?",
                    (_now_iso(), record_id),
                )
            conn.commit()
        finally:
            conn.close()
    if hard and rel:
        try:
            p = Path(brain) / rel
            if p.is_file() and "wiki/knowledge/" in rel.replace("\\", "/"):
                p.unlink()
        except OSError:
            pass
    return {"ok": True, "id": record_id, "hard": hard}


def correct(brain: str | Path, record_id: str, new_text: str, *, title: str = "") -> dict[str, Any]:
    """User correction: bump version, keep provenance, re-hash."""
    brain = Path(brain)
    body = (new_text or "").strip()
    if not body:
        return {"ok": False, "error": "empty text"}
    now = _now_iso()
    ch = _sha(body)
    with _LOCK:
        conn = _connect(brain)
        try:
            row = conn.execute(
                "SELECT * FROM records WHERE id=? AND deleted=0", (record_id,)
            ).fetchone()
            if not row:
                return {"ok": False, "error": "not found"}
            ver = int(row["version"] or 1) + 1
            new_title = (title or row["title"] or "").strip()
            conn.execute(
                """
                UPDATE records SET body=?, content_hash=?, title=?, version=?,
                    updated_at=?, outdated=0, verified=1
                WHERE id=?
                """,
                (body, ch, new_title, ver, now, record_id),
            )
            conn.commit()
            rel = row["relative_path"] or ""
        finally:
            conn.close()
    if rel:
        try:
            p = Path(brain) / rel
            if p.is_file():
                ingest_meta = (
                    f"---\nid: {record_id}\ntitle: {json.dumps(new_title, ensure_ascii=False)}\n"
                    f"version: {ver}\nupdated: {now}\n---\n\n# {new_title}\n\n{body}\n"
                )
                p.write_text(ingest_meta, encoding="utf-8")
        except OSError:
            pass
    return {"ok": True, "id": record_id, "version": ver, "content_hash": ch}


def stats(brain: str | Path) -> dict[str, Any]:
    brain = Path(brain)
    with _LOCK:
        conn = _connect(brain)
        try:
            total = conn.execute("SELECT COUNT(*) c FROM records WHERE deleted=0").fetchone()["c"]
            outdated = conn.execute(
                "SELECT COUNT(*) c FROM records WHERE deleted=0 AND outdated=1"
            ).fetchone()["c"]
            verified = conn.execute(
                "SELECT COUNT(*) c FROM records WHERE deleted=0 AND verified=1"
            ).fetchone()["c"]
            kinds = {
                r["kind"]: r["c"]
                for r in conn.execute(
                    "SELECT kind, COUNT(*) c FROM records WHERE deleted=0 GROUP BY kind"
                )
            }
        finally:
            conn.close()
    wiki_n = 0
    wk = Path(brain) / "wiki" / "knowledge"
    if wk.is_dir():
        wiki_n = len(list(wk.glob("*.md")))
    return {
        "ok": True,
        "schema": SCHEMA_VERSION,
        "records": total,
        "outdated": outdated,
        "verified": verified,
        "kinds": kinds,
        "wiki_knowledge_notes": wiki_n,
        "db": str(_db_path(brain)),
    }


def answer_packet(brain: str | Path, query: str, limit: int = 6) -> dict[str, Any]:
    """Packet for agents: search + citation rules + insufficiency flag."""
    res = search(brain, query, limit=limit)
    if not res.get("ok"):
        return res
    hits = res.get("hits") or []
    mem = [m for m in (res.get("memory_index") or []) if not m.get("error")]
    insufficient = not hits and not mem
    citations = []
    for h in hits:
        citations.append(
            {
                "id": h["id"],
                "path": h.get("relative_path") or "",
                "source_uri": h.get("source_uri") or "",
                "verified": h.get("verified"),
                "outdated": h.get("outdated"),
            }
        )
    return {
        "ok": True,
        "query": query,
        "insufficient": insufficient,
        "hits": hits,
        "memory_index": mem,
        "citations": citations,
        "instructions": (
            "Distinguish verified facts from inference. Cite paths. "
            "If insufficient=true, say you do not know yet and offer to learn/ingest."
        ),
    }


OPS = (
    "search",
    "ingest",
    "get",
    "forget",
    "correct",
    "stats",
    "answer",
)


def run(args: dict, vault_root: str) -> str:
    """MCP/plugin entry — returns JSON text for the model."""
    op = str((args or {}).get("op") or "").strip()
    if not vault_root:
        return json.dumps({"ok": False, "error": "no brain"}, ensure_ascii=False)
    if op not in OPS:
        return json.dumps({"ok": False, "error": f"op must be one of {OPS}"}, ensure_ascii=False)
    brain = Path(vault_root)
    try:
        if op == "search":
            out = search(brain, str(args.get("query") or ""), limit=int(args.get("limit") or 8))
        elif op == "answer":
            out = answer_packet(brain, str(args.get("query") or ""), limit=int(args.get("limit") or 6))
        elif op == "ingest":
            out = ingest(
                brain,
                text=str(args.get("text") or ""),
                title=str(args.get("title") or ""),
                kind=str(args.get("kind") or "fact"),
                source_uri=str(args.get("source_uri") or ""),
                source_type=str(args.get("source_type") or "chat"),
                tags=list(args.get("tags") or []) if isinstance(args.get("tags"), list) else [],
                confidence=float(args.get("confidence") or 0.6),
                verified=bool(args.get("verified")),
            )
        elif op == "get":
            out = get_record(brain, str(args.get("id") or ""))
        elif op == "forget":
            out = forget(brain, str(args.get("id") or ""), hard=bool(args.get("hard")))
        elif op == "correct":
            out = correct(
                brain,
                str(args.get("id") or ""),
                str(args.get("text") or ""),
                title=str(args.get("title") or ""),
            )
        else:
            out = stats(brain)
    except Exception as e:  # noqa: BLE001
        out = {"ok": False, "error": f"{type(e).__name__}: {e}"}
    return json.dumps(out, ensure_ascii=False, indent=2)
