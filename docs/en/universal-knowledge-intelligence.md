# Universal Knowledge Intelligence Engine (phase 1)

Markdown Second Brain remains the source of truth. This layer adds provenance, dedupe, versioning metadata, hybrid retrieve, and MCP/REST access — without installing RAGFlow / LlamaIndex / Mem0 as a second stack.

## Audit

| Layer | Existing |
|---|---|
| Sources → INGEST → Wiki | Second Brain docs / ingest upload |
| Long-term memory | `memory/` + `memory_index.py` |
| Wikilink graph | Knowledge graph page |
| Chat memory tools | `javis_memory` |
| New provenance store | `.javis/knowledge/intel.sqlite3` + `wiki/knowledge/*.md` |

## Selected stack

- SoT: vault Markdown  
- Index: SQLite (knowledge_intel) + existing MemoryIndex cascade  
- Optional later sidecars: pgvector/Qdrant, Docling/MarkItDown workers (not on Vercel)  
- Eval: reuse improvement qualification; optional RAGAS later  

## APIs / MCP

- `GET /knowledge/stats`, `POST /knowledge/search`, `POST /knowledge/ingest`  
- Tool `javis_knowledge` (`search|answer|ingest|get|correct|forget|stats`)  

## Intelligence rules

- Cite `relative_path` / `source_uri`  
- `outdated=true` → treat as historical  
- `insufficient=true` → admit unknown  
- User `correct` / `forget` always available  

See also: [autonomous-self-evolving.md](./autonomous-self-evolving.md), [13-second-brain.md](./13-second-brain.md).
