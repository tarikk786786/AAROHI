"""Bundled plugin: knowledge intelligence (provenance + hybrid retrieve)."""
from __future__ import annotations

import asyncio

import knowledge_intel


def register(ctx):
    ctx.register_tool(
        "javis_knowledge",
        "Knowledge intelligence for this brain. "
        "op=answer|search {query}: hybrid retrieve with citations. "
        "op=ingest {text, title?, source_uri?}: dedupe + version + wiki note. "
        "op=get|correct|forget {id}: read / user-correct / delete. "
        "op=stats: counts. Admit insufficient knowledge when answer.insufficient=true.",
        _run,
        schema={
            "type": "object",
            "properties": {
                "op": {"type": "string", "enum": list(knowledge_intel.OPS)},
                "query": {"type": "string"},
                "text": {"type": "string"},
                "title": {"type": "string"},
                "kind": {"type": "string"},
                "source_uri": {"type": "string"},
                "source_type": {"type": "string"},
                "id": {"type": "string"},
                "limit": {"type": "integer"},
                "hard": {"type": "boolean"},
                "verified": {"type": "boolean"},
                "confidence": {"type": "number"},
                "tags": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["op"],
        },
        min_mode="safe",
        emoji="📚",
    )


async def _run(args, ctx) -> str:
    return await asyncio.to_thread(
        knowledge_intel.run, args or {}, getattr(ctx, "vault_root", "") or ""
    )
