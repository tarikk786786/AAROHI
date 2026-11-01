"""Bundled plugin: self-evolve experience facade (owner sessions).

Does not deploy skills. Points agents at existing Self-learning + improvement candidates.
"""
from __future__ import annotations

import asyncio

import self_evolve


def register(ctx):
    ctx.register_tool(
        "javis_evolve",
        "Self-evolve experience log and research proposals for this brain. "
        "op=status: learning/improvement authority map + metrics. "
        "op=record {event_type, summary, ...}: log task_success|task_failure|user_correction|tool_error|... "
        "op=list: recent experiences. op=metrics: daily counters. "
        "op=propose_research {title, repo_url, rationale}: queue a repo idea — NEVER clones. "
        "op=decide_research {id, approve}: owner marks proposal reviewed. "
        "To deploy a skill candidate use Self-learning / Improvement UI — this tool cannot apply code.",
        _run,
        schema={
            "type": "object",
            "properties": {
                "op": {"type": "string", "enum": list(self_evolve.OPS)},
                "event_type": {"type": "string"},
                "summary": {"type": "string"},
                "detail": {"type": "string"},
                "skill_slug": {"type": "string"},
                "tool_name": {"type": "string"},
                "success": {"type": "boolean"},
                "tokens": {"type": "integer"},
                "latency_ms": {"type": "integer"},
                "cost_usd": {"type": "number"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "limit": {"type": "integer"},
                "days": {"type": "integer"},
                "title": {"type": "string"},
                "repo_url": {"type": "string"},
                "rationale": {"type": "string"},
                "license_note": {"type": "string"},
                "id": {"type": "string"},
                "approve": {"type": "boolean"},
            },
            "required": ["op"],
        },
        min_mode="safe",
        emoji="🧬",
    )


async def _run(args, ctx) -> str:
    return await asyncio.to_thread(
        self_evolve.run, args or {}, getattr(ctx, "vault_root", "") or ""
    )
