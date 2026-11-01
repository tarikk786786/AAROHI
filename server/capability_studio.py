"""AAROHI Capability Studio - unified registry over skills, plugins, MCP, packs, services.

Does not replace existing loaders. Aggregates live state from skill_router, plugins_host,
mcp_store/mcp_hub, packs, and lightweight service health probes so the browser Studio can
manage the capability ecosystem without rebuilding the app.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import localefmt

GITHUB_RE = re.compile(
    r"^https?://(?:www\.)?github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?(?:/tree/(?P<ref>[^/]+)/(?P<path>.+))?/?$",
    re.I,
)


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def registry(brain_root: str, brain_id: str = "brain") -> dict:
    """One authoritative snapshot of every capability visible to this brain."""
    items: List[dict] = []
    items.extend(_skills(brain_root))
    items.extend(_plugins(brain_root))
    items.extend(_mcp())
    items.extend(_packs())
    items.extend(_services())
    counts: Dict[str, int] = {}
    for it in items:
        counts[it["type"]] = counts.get(it["type"], 0) + 1
    return {
        "ok": True,
        "brain": brain_id,
        "generated_at": _now(),
        "counts": counts,
        "items": items,
        "studio": {
            "modules": [
                "overview", "skills", "plugins", "mcp", "repostore",
                "packs", "services", "agents", "workflows", "learn", "versions", "security",
            ],
            "note": "Edits go through existing /skills, /plugins authoring, /mcp, /packs routes; "
                    "this registry only aggregates and never executes foreign code.",
        },
    }


def _skills(brain_root: str) -> List[dict]:
    out = []
    try:
        import skill_router
        for s in skill_router.list_skills(brain_root) or []:
            slug = s.get("slug") or s.get("name") or ""
            out.append({
                "id": f"skill:{slug}",
                "type": "skill",
                "display_name": s.get("name") or slug,
                "description": (s.get("description") or "")[:300],
                "version": s.get("version") or "",
                "source": s.get("source") or "brain",
                "repository": s.get("repository") or "",
                "license": s.get("license") or "",
                "installed": True,
                "enabled": not bool(s.get("disabled")),
                "runtime": "skill.md",
                "dependencies": [],
                "permission": "prompt",
                "health": "ready" if not s.get("disabled") else "disabled",
                "updated": s.get("mtime") or "",
                "revision": "",
                "stats": {"use": s.get("use") or 0},
                "meta": {"group": s.get("group") or "", "slug": slug, "system": bool(s.get("system"))},
            })
    except Exception as e:
        out.append(_err_item("skill", "skills", str(e)))
    return out


def _plugins(brain_root: str) -> List[dict]:
    out = []
    try:
        import plugins_host
        for p in plugins_host.describe(brain_root) or []:
            slug = p.get("slug") or ""
            src = p.get("source") or ""
            editable = src in ("user", "vault")
            health = "error" if p.get("error") else (
                "ready" if p.get("enabled") and p.get("loaded") else
                ("disabled" if not p.get("enabled") else "idle")
            )
            out.append({
                "id": f"plugin:{slug}",
                "type": "plugin",
                "display_name": p.get("name") or slug,
                "description": (p.get("description") or "")[:300],
                "version": p.get("version") or "",
                "source": src,
                "repository": "",
                "license": "",
                "installed": not bool(p.get("removed")),
                "enabled": bool(p.get("enabled")),
                "runtime": "python-plugin",
                "dependencies": [],
                "permission": p.get("min_mode") or "safe",
                "health": health,
                "updated": "",
                "revision": "",
                "stats": {"tools": len(p.get("tools") or [])},
                "meta": {
                    "slug": slug,
                    "tools": p.get("tools") or [],
                    "hooks": p.get("hooks") or [],
                    "editable": editable,
                    "error": p.get("error") or "",
                    "gated": bool(p.get("gated")),
                },
            })
    except Exception as e:
        out.append(_err_item("plugin", "plugins", str(e)))
    return out


def _mcp() -> List[dict]:
    out = []
    try:
        import mcp_store
        for c in (mcp_store.list_connections() or []):
            cid = c.get("id") or c.get("name") or ""
            enabled = bool(c.get("enabled", True))
            out.append({
                "id": f"mcp:{cid}",
                "type": "mcp",
                "display_name": c.get("name") or cid,
                "description": (c.get("description") or c.get("command") or "")[:300],
                "version": "",
                "source": c.get("transport") or c.get("type") or "mcp",
                "repository": "",
                "license": "",
                "installed": True,
                "enabled": enabled,
                "runtime": "mcp",
                "dependencies": [],
                "permission": c.get("mode") or c.get("strict") or "full",
                "health": "ready" if enabled else "disabled",
                "updated": "",
                "revision": "",
                "stats": {},
                "meta": {"id": cid, "url": c.get("url") or "", "command": c.get("command") or ""},
            })
    except Exception as e:
        out.append(_err_item("mcp", "mcp", str(e)))
    return out


def _packs() -> List[dict]:
    out = []
    try:
        import packs
        listed = []
        if hasattr(packs, "list_installed"):
            listed = packs.list_installed() or []
        elif hasattr(packs, "danh_sach"):
            listed = packs.danh_sach() or []
        for p in listed:
            pid = p.get("id") or p.get("slug") or p.get("name") or ""
            out.append({
                "id": f"pack:{pid}",
                "type": "pack",
                "display_name": p.get("name") or pid,
                "description": (p.get("description") or "")[:300] if isinstance(p.get("description"), str)
                else str((p.get("description") or {}).get("en") or "")[:300],
                "version": p.get("version") or "",
                "source": "store",
                "repository": p.get("repo") or p.get("repository") or "",
                "license": p.get("license") or "",
                "installed": True,
                "enabled": bool(p.get("enabled", True)),
                "runtime": "extension-pack",
                "dependencies": p.get("depends") or [],
                "permission": "pack",
                "health": "ready" if p.get("enabled", True) else "disabled",
                "updated": p.get("updated") or "",
                "revision": p.get("sha") or p.get("commit") or "",
                "stats": {},
                "meta": {"id": pid},
            })
    except Exception as e:
        out.append(_err_item("pack", "packs", str(e)))
    return out


def _services() -> List[dict]:
    """Independent backend-ish services AAROHI already runs (health only, no start/stop yet)."""
    services = [
        _svc("hub", "MCP Hub", "Tool routing and MCP sessions", _probe_hub),
        _svc("tts", "Voice / TTS", "Speech synthesis provider", _probe_tts),
        _svc("scheduler", "Task scheduler", "Reminders, loops, Kanban", _probe_sched),
        _svc("plugins-host", "Plugin host", "Native Python plugins", _probe_plugins_host),
        _svc("brain-git", "Brain git history", "Skill/plugin revision storage", _probe_git),
    ]
    return services


def _svc(sid: str, name: str, desc: str, probe) -> dict:
    try:
        health, meta = probe()
    except Exception as e:
        health, meta = "error", {"error": str(e)[:200]}
    return {
        "id": f"service:{sid}",
        "type": "service",
        "display_name": name,
        "description": desc,
        "version": "",
        "source": "aarohi",
        "repository": "",
        "license": "Apache-2.0 / MIT upstream notices apply",
        "installed": True,
        "enabled": health not in ("unavailable",),
        "runtime": "process",
        "dependencies": [],
        "permission": "system",
        "health": health,
        "updated": _now(),
        "revision": "",
        "stats": {},
        "meta": meta,
    }


def _probe_hub():
    import mcp_hub
    n = 0
    try:
        # Prefer a cheap status if present; otherwise assume alive if import works.
        if hasattr(mcp_hub, "route_count"):
            n = int(mcp_hub.route_count() or 0)
        elif hasattr(mcp_hub, "list_tools_cached"):
            n = len(mcp_hub.list_tools_cached() or [])
    except Exception:
        pass
    return "ready", {"tools_hint": n}


def _probe_tts():
    key = bool(os.getenv("ELEVENLABS_API_KEY") or "")
    edge = True  # Edge TTS is default free path in AAROHI
    return ("ready" if edge or key else "unavailable"), {
        "edge_tts": edge,
        "elevenlabs_configured": key,
        "default": "edge-tts / openai-compat fallbacks",
    }


def _probe_sched():
    serverless = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
    if serverless:
        return "degraded", {"note": "Serverless host: background loops limited; use persistent VPS for full services."}
    return "ready", {"note": "In-process scheduler"}


def _probe_plugins_host():
    import plugins_host
    return "ready", {"user_plugins_env": plugins_host._env_user_enabled()}


def _probe_git():
    try:
        import git_brain
        return "ready", {"module": "git_brain"}
    except Exception:
        return "idle", {"note": "git_brain optional"}


def _err_item(typ: str, name: str, err: str) -> dict:
    return {
        "id": f"{typ}:__error__",
        "type": typ,
        "display_name": name,
        "description": err[:300],
        "version": "",
        "source": "error",
        "repository": "",
        "license": "",
        "installed": False,
        "enabled": False,
        "runtime": "",
        "dependencies": [],
        "permission": "",
        "health": "error",
        "updated": _now(),
        "revision": "",
        "stats": {},
        "meta": {"error": err},
    }


def inspect_repository(url: str) -> dict:
    """Inspect a GitHub URL without downloading or executing code.

    Returns component guesses (skill / plugin / mcp / pack / unknown), license hint,
    and whether self-hosting looks plausible. Never installs.
    """
    url = (url or "").strip()
    if not url:
        return {"ok": False, "error": localefmt.chu("Thiếu URL", "Missing URL")}
    m = GITHUB_RE.match(url.split("?")[0].rstrip("/"))
    if not m:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return {"ok": False, "error": localefmt.chu("Chỉ hỗ trợ http(s)", "Only http(s) URLs are supported")}
        return {
            "ok": True,
            "url": url,
            "kind_guess": "unknown",
            "host": parsed.netloc,
            "review_required": True,
            "security": ["Non-GitHub URL: manual review required before any install."],
            "compatible": False,
            "message": localefmt.chu(
                "Chưa tự nhận diện được. Dán URL GitHub skill/plugin/MCP để soi sâu hơn.",
                "Could not auto-detect. Paste a GitHub skill/plugin/MCP URL for a deeper inspect.",
            ),
        }

    owner, repo, ref, path = m.group("owner"), m.group("repo"), m.group("ref") or "", m.group("path") or ""
    meta = _github_repo_meta(owner, repo)
    files_hint = _github_path_hint(owner, repo, ref or meta.get("default_branch") or "main", path)
    kind = _guess_kind(path, files_hint, meta)
    license_spdx = (meta.get("license") or {}).get("spdx_id") if isinstance(meta.get("license"), dict) else ""
    return {
        "ok": True,
        "url": url,
        "owner": owner,
        "repo": repo,
        "ref": ref or meta.get("default_branch") or "",
        "path": path,
        "kind_guess": kind,
        "description": meta.get("description") or "",
        "stars": meta.get("stargazers_count"),
        "license": license_spdx or "",
        "default_branch": meta.get("default_branch") or "",
        "language": meta.get("language") or "",
        "archived": bool(meta.get("archived")),
        "files_hint": files_hint[:40],
        "install_targets": _targets_for(kind),
        "credentials_likely": _creds_for(kind),
        "self_host": True,
        "compatible": kind in ("skill", "plugin", "mcp", "pack"),
        "review_required": True,
        "security": _security_notes(kind, meta),
        "message": localefmt.chu(
            "Đã soi repository. Không cài gì cả - hãy duyệt rồi chọn Import vào Skills/Plugins/MCP/Packs.",
            "Repository inspected. Nothing was installed - review, then Import into Skills/Plugins/MCP/Packs.",
        ),
        "inspected_at": _now(),
        "content_fingerprint": hashlib.sha256(
            json.dumps({"o": owner, "r": repo, "p": path, "f": files_hint[:20]}, sort_keys=True).encode()
        ).hexdigest()[:16],
    }


def _github_repo_meta(owner: str, repo: str) -> dict:
    return _http_json(f"https://api.github.com/repos/{owner}/{repo}") or {}


def _github_path_hint(owner: str, repo: str, ref: str, path: str) -> List[str]:
    if path:
        api = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={ref}"
        data = _http_json(api)
        if isinstance(data, list):
            return [x.get("name") for x in data if isinstance(x, dict) and x.get("name")]
        if isinstance(data, dict) and data.get("name"):
            return [data["name"]]
        return []
    # Root listing (shallow)
    data = _http_json(f"https://api.github.com/repos/{owner}/{repo}/contents/?ref={ref}")
    if isinstance(data, list):
        return [x.get("name") for x in data if isinstance(x, dict) and x.get("name")]
    return []


def _http_json(url: str) -> Any:
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "AAROHI-CapabilityStudio/1.0",
    })
    token = (os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN") or "").strip()
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, json.JSONDecodeError):
        return None


def _guess_kind(path: str, files: List[str], meta: dict) -> str:
    names = {f.lower() for f in files}
    path_l = (path or "").lower()
    if "skill.md" in names or path_l.endswith("skill.md") or "/skills/" in f"/{path_l}/":
        return "skill"
    if "plugin.yaml" in names or "plugin.yml" in names or "plugin.py" in names:
        return "plugin"
    if "pack.yaml" in names or "pack.yml" in names or "javis.pack" in names:
        return "pack"
    if any(x in names for x in ("mcp.json", "server.py", "index.js", "package.json")) and (
        "mcp" in path_l or "mcp" in (meta.get("description") or "").lower()
        or "mcp" in (meta.get("name") or "").lower()
    ):
        return "mcp"
    if "mcp" in path_l:
        return "mcp"
    return "unknown"


def _targets_for(kind: str) -> List[str]:
    return {
        "skill": ["skills"],
        "plugin": ["plugins"],
        "mcp": ["mcp"],
        "pack": ["packs"],
        "unknown": ["skills", "plugins", "mcp", "packs", "libraries"],
    }.get(kind, ["skills", "plugins", "mcp", "packs"])


def _creds_for(kind: str) -> List[str]:
    if kind == "mcp":
        return ["May require OAuth or API keys for the upstream service"]
    if kind == "plugin":
        return ["May declare secrets in plugin.yaml - keep them server-side"]
    return []


def _security_notes(kind: str, meta: dict) -> List[str]:
    notes = [
        "Never auto-execute downloaded third-party code.",
        "Staged install + human approval required for executable plugins.",
    ]
    if meta.get("archived"):
        notes.append("Upstream repository is archived.")
    if kind == "unknown":
        notes.append("Component type unclear - inspect files before import.")
    return notes


def services_detail() -> dict:
    return {"ok": True, "services": _services(), "generated_at": _now()}
