"""AAROHI Universal Brain - free-first wake-up and openai-compat failover.

When LLM7 returns 401 (bad key) or 429 (daily quota), clear the bad key / rotate to the
next verified anonymous OpenAI-compatible endpoint so chat keeps working without paid APIs.

Never invent API keys. Prefer keyless endpoints that were smoke-tested, then env-keyed free
tiers (Groq / Gemini / OpenRouter) already seeded by apply_model_env.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

import localefmt

# Ordered free openai-compat endpoints (anonymous / no key). Keep llm7 first; OVH is proven live.
_FREE_ANON_CHAIN = (
    {
        "id": "llm7",
        "base_url": "https://api.llm7.io/v1",
        "model": "turbo",
        "anonymous": True,
    },
    {
        "id": "ovh-anonymous",
        "base_url": "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1",
        "model": "Meta-Llama-3_3-70B-Instruct",
        "anonymous": True,
    },
)


def _keyed_compat_chain() -> list:
    """Optional OpenAI-compatible backends from env (NVIDIA NIM, Hugging Face). Never hardcode secrets."""
    out = []
    nkey = (os.getenv("NVIDIA_API_KEY") or "").strip()
    if nkey:
        out.append({
            "id": "nvidia-nim",
            "base_url": (os.getenv("NVIDIA_BASE_URL") or "https://integrate.api.nvidia.com/v1").rstrip("/"),
            "model": (os.getenv("NVIDIA_MODEL") or "meta/llama-3.1-8b-instruct").strip(),
            "anonymous": False,
            "key_env": "NVIDIA_API_KEY",
        })
    hf = (os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_KEY") or "").strip()
    if hf:
        out.append({
            "id": "huggingface",
            "base_url": (os.getenv("HF_BASE_URL") or "https://router.huggingface.co/v1").rstrip("/"),
            "model": (os.getenv("HF_MODEL") or "meta-llama/Meta-Llama-3-8B-Instruct").strip(),
            "anonymous": False,
            "key_env": "HF_TOKEN",
        })
    return out

_STATE_NAME = "universal_brain.json"


def _presets_path() -> Path:
    return Path(__file__).resolve().parent.parent / "system" / "free-llm-presets.json"


def _state_path():
    try:
        import config as cfgmod
        return Path(cfgmod.STATE_DIR) / _STATE_NAME
    except Exception:
        return Path("/tmp") / _STATE_NAME


def _load_state() -> dict:
    try:
        return json.loads(_state_path().read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_state(data: dict) -> None:
    try:
        p = _state_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"[universal-brain] state save: {e}", file=sys.stderr)


def free_anon_chain() -> list:
    """Anonymous free endpoints + optional env-keyed NVIDIA/HF openai-compat backends."""
    out = list(_FREE_ANON_CHAIN)
    seen = {x["base_url"].rstrip("/") for x in out}
    try:
        data = json.loads(_presets_path().read_text(encoding="utf-8"))
        for p in data.get("presets") or []:
            if not p.get("anonymous"):
                continue
            if p.get("aarohi_provider") != "openai-compat":
                continue
            base = (p.get("base_url") or "").strip().rstrip("/")
            if not base or base in seen:
                continue
            models = p.get("models") or ["turbo"]
            out.append({"id": p.get("id") or base, "base_url": base,
                        "model": models[0], "anonymous": True})
            seen.add(base)
    except Exception:
        pass
    for item in _keyed_compat_chain():
        base = item["base_url"].rstrip("/")
        if base in seen:
            continue
        out.append(item)
        seen.add(base)
    return out


def _apply_compat_endpoint(m: dict, item: dict) -> None:
    """Point openai-compat at one chain item (anonymous or keyed from env)."""
    m["openai_compat_base"] = item["base_url"]
    m.setdefault("profiles", {}).setdefault("openai-compat", {})["model"] = item["model"]
    if item.get("anonymous"):
        m["openai_compat_key"] = ""
    else:
        env_name = item.get("key_env") or ""
        m["openai_compat_key"] = (os.getenv(env_name) or "").strip() if env_name else ""


def _is_auth(raw: str) -> bool:
    try:
        import aux_engine
        return aux_engine.is_auth_failure(raw)
    except Exception:
        low = (raw or "").lower()
        return "401" in low or "invalid" in low or "authentication" in low


def _is_quota(raw: str) -> bool:
    try:
        import aux_engine
        return aux_engine.is_quota_exhaustion(raw)
    except Exception:
        low = (raw or "").lower()
        return "429" in low or "quota" in low


def wake_free_brain(mcfg: Optional[dict] = None) -> dict:
    """Ensure openai-compat points at a working anonymous free endpoint (no fake keys).

    Clears an invalid openai_compat_key so LLM7 anonymous works again.
    """
    import config as cfgmod
    import model_routing

    cfg = cfgmod.read_settings()
    m = cfg.setdefault("model", {})
    if mcfg is not None:
        m.update({k: mcfg[k] for k in mcfg if k.startswith("openai_compat") or k in ("order", "main", "engine", "profiles")})

    changed = False
    key = str(m.get("openai_compat_key") or "").strip()
    # Bad leftover keys cause 401; anonymous LLM7 needs an empty key.
    if key and key.lower() not in ("none", "local", "anonymous"):
        # Keep env override if owner explicitly set OPENAI_COMPAT_KEY; otherwise clear for wake-up.
        env_key = (os.getenv("OPENAI_COMPAT_KEY") or "").strip()
        if not env_key or key != env_key:
            m["openai_compat_key"] = ""
            changed = True
        # If env itself is the bad key, still clear settings so anonymous can run until they fix env.
        elif _load_state().get("last_auth_fail"):
            m["openai_compat_key"] = ""
            changed = True

    base = str(m.get("openai_compat_base") or "").strip().rstrip("/")
    chain = free_anon_chain()
    if not base:
        pick = chain[0]
        m["openai_compat_base"] = pick["base_url"]
        m.setdefault("profiles", {}).setdefault("openai-compat", {})["model"] = pick["model"]
        changed = True
        base = pick["base_url"]

    # Lift rest so the card can run after we fixed the key/base.
    try:
        model_routing.clear_rest("openai-compat", "-")
    except Exception:
        pass

    # Ensure openai-compat is in usage order (MAIN if nothing else).
    order = [str(x).strip() for x in (m.get("order") or []) if str(x).strip()]
    has_other = any(p for p in order if p != "openai-compat") or any(
        str(m.get(f) or "").strip() for f in (
            "openrouter_key", "groq_api_key", "gemini_api_key", "openai_api_key", "anthropic_api_key",
        )
    )
    if "openai-compat" not in order:
        order = (["openai-compat"] + order) if not has_other else (order + ["openai-compat"])
        m["order"] = order
        changed = True
    main_prov = str((m.get("main") or {}).get("provider") or "").strip()
    if not main_prov or main_prov in ("anthropic-cli", "openai-oauth", "grok-cli"):
        model = ((m.get("profiles") or {}).get("openai-compat") or {}).get("model") or "turbo"
        m["main"] = {"provider": "openai-compat", "model": model}
        m["engine"] = "openai-compat"
        changed = True

    if changed:
        cfg["model"] = m
        cfgmod.write_settings(cfg)
        print("[universal-brain] free brain awake "
              f"base={m.get('openai_compat_base')} key={'set' if m.get('openai_compat_key') else 'anonymous'}",
              file=sys.stderr)
    return {
        "ok": True,
        "changed": changed,
        "base": m.get("openai_compat_base"),
        "anonymous": not bool(str(m.get("openai_compat_key") or "").strip()),
        "model": ((m.get("profiles") or {}).get("openai-compat") or {}).get("model") or "",
        "order": m.get("order") or [],
    }


def on_provider_rest(mcfg: dict, provider: str, raw: str, seconds: float = 0) -> dict:
    """Called when openai-compat (or similar) is put to rest after 401/429."""
    if provider != "openai-compat":
        return {"ok": True, "action": "noop"}
    import config as cfgmod
    import model_routing

    st = _load_state()
    cfg = cfgmod.read_settings()
    m = cfg.setdefault("model", {})
    # Prefer live mcfg fields if present.
    if mcfg:
        for k in ("openai_compat_base", "openai_compat_key"):
            if k in mcfg:
                m[k] = mcfg[k]

    action = "rest"
    if _is_auth(raw):
        st["last_auth_fail"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        st["last_auth_raw"] = (raw or "")[:240]
        # Drop invalid key → anonymous LLM7 often still works.
        if str(m.get("openai_compat_key") or "").strip():
            m["openai_compat_key"] = ""
            action = "cleared_bad_key"
        # If still on a failing host, rotate to next anonymous endpoint.
        cur = str(m.get("openai_compat_base") or "").strip().rstrip("/")
        chain = free_anon_chain()
        nxt = None
        for i, item in enumerate(chain):
            if item["base_url"].rstrip("/") == cur:
                nxt = chain[(i + 1) % len(chain)] if len(chain) > 1 else None
                break
        if nxt is None and chain:
            nxt = chain[0]
        if nxt and nxt["base_url"].rstrip("/") != cur:
            _apply_compat_endpoint(m, nxt)
            action = "rotated_compat"
            st["active_preset"] = nxt["id"]
        # Auth fix should unlock the card immediately for the next hop / next turn.
        try:
            model_routing.clear_rest("openai-compat", "-")
        except Exception:
            pass
        cfg["model"] = m
        cfgmod.write_settings(cfg)
        _save_state(st)
        print(f"[universal-brain] {action} after auth fail → {m.get('openai_compat_base')}",
              file=sys.stderr)
        return {"ok": True, "action": action, "base": m.get("openai_compat_base"),
                "tell_owner": localefmt.chu(
                    "Key OpenAI Compatible cũ không còn hợp lệ - AAROHI đã chuyển sang free anonymous.",
                    "The OpenAI Compatible key was invalid - AAROHI switched to a free anonymous brain.")}

    if _is_quota(raw):
        st["last_quota_fail"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        cur = str(m.get("openai_compat_base") or "").strip().rstrip("/")
        chain = free_anon_chain()
        for i, item in enumerate(chain):
            if item["base_url"].rstrip("/") == cur and len(chain) > 1:
                nxt = chain[(i + 1) % len(chain)]
                _apply_compat_endpoint(m, nxt)
                st["active_preset"] = nxt["id"]
                cfg["model"] = m
                cfgmod.write_settings(cfg)
                try:
                    model_routing.clear_rest("openai-compat", "-")
                except Exception:
                    pass
                _save_state(st)
                print(f"[universal-brain] rotated after quota → {nxt['base_url']}", file=sys.stderr)
                return {"ok": True, "action": "rotated_compat_quota", "base": nxt["base_url"],
                        "tell_owner": localefmt.chu(
                            "Free LLM trước hết hạn mức - đã chuyển endpoint free khác.",
                            "The previous free LLM hit its limit - switched to another free endpoint.")}
                break
        _save_state(st)
    return {"ok": True, "action": action}


def status() -> dict:
    import config as cfgmod
    m = (cfgmod.read_settings().get("model") or {})
    st = _load_state()
    return {
        "ok": True,
        "mode": "free-first",
        "openai_compat_base": m.get("openai_compat_base") or "",
        "anonymous": not bool(str(m.get("openai_compat_key") or "").strip()),
        "order": m.get("order") or [],
        "main": m.get("main") or {},
        "chain": free_anon_chain(),
        "state": st,
        "get_free_keys": {
            "groq": "https://console.groq.com/keys",
            "gemini": "https://aistudio.google.com/app/apikey",
            "openrouter": "https://openrouter.ai/keys",
            "llm7_token": "https://token.llm7.io",
            "nvidia": "https://build.nvidia.com/",
            "huggingface": "https://huggingface.co/settings/tokens",
        },
        "env_brains": {
            "groq": bool((os.getenv("GROQ_API_KEY") or "").strip()),
            "nvidia": bool((os.getenv("NVIDIA_API_KEY") or "").strip()),
            "huggingface": bool((os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_KEY") or "").strip()),
            "github": bool((os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN") or "").strip()),
        },
        "note": "Secrets live in gitignored .env / Vercel env only. Anonymous free + keyed Groq/NVIDIA/HF; GitHub tokens are for git/MCP, not chat.",
    }
