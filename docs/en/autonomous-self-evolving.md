# Autonomous Self-Learning & Self-Evolving Engine (AAROHI)

## 1. Existing architecture audit

AAROHI **already ships** a production self-learning and skill-evolution stack. This project does **not** install AutoSkill / DSPy / Mem0 / ACE as a second framework.

| Need | Existing owner |
|---|---|
| Chat → memory/wiki/skill extract | `learn.py`, `auto_learning.py`, **Self-learning** page |
| Model cannot write files during learn | JSON extract → Python writer only |
| Secret + injection scans | learn path scanners |
| Git undo of learning commits | `git_brain.py` |
| Skill evolution with measurable baseline | `improvement_loop.py` (Harness²) |
| Candidates, authorize, apply | `improvement_candidate_*` + dashboard JS |
| Experiments / canary | `improvement_experiment_*`, `improvement_canary.py` |
| Sandbox / limits | `improvement_sandbox.py`, execution limits |
| Memory correction from chat | `javis_memory` plugin |
| Knowledge provenance (new) | `knowledge_intel.py` + `javis_knowledge` |
| Experience metrics facade (new) | `self_evolve.py` + `javis_evolve` |

Dashboard: **Brain → Self-learning** plus Improvement Candidates / Experiments panels (`improvement-candidates.js`).

## 2. Repository comparison (selected)

See [`system/self-evolve-registry.json`](../../system/self-evolve-registry.json).

| Repo | Verdict |
|---|---|
| AutoSkill, Memento-Skills, MemSkill, SkillHone, GEPA | Study patterns only |
| ACE | Reject as core (duplicate orchestration) |
| mem0 | Optional sidecar — vault is SoT |
| graphiti | Optional later temporal KG |
| DSPy | Optional research; do not replace `improvement_loop` |
| Langfuse | Optional ops observability |
| DeepEval / promptfoo | Optional CI beside sealed qualification |

## 3. Selected technology stack

- **SoT**: Markdown vault (`memory/`, `wiki/`, `skills/`)
- **Learn writer**: Python (`learn.py`) after isolated model extract
- **Skill evolution**: `improvement_loop` + qualification vs baseline
- **Approval**: Owner authorize — `CAPABILITIES.activation` remains false for auto-activation
- **Experience log**: SQLite under `.javis/self_evolve/`
- **Knowledge intel**: SQLite + `wiki/knowledge/` notes
- **Workers**: Local/Docker for continuous loops — **not** Vercel serverless

## 4. Continuous loop (enforced)

`OBSERVE → ANALYZE → EXTRACT → LEARN → GENERATE → TEST → COMPARE → APPROVE → DEPLOY → MONITOR`

Promotion rule: **candidate must beat baseline on sealed cases**. An LLM saying “better” is never enough.

## 5. Safety & governance

- No automatic execution of downloaded code  
- No arbitrary production code modification  
- Research proposals are queued only (`javis_evolve` / `propose_research`)  
- Rollback via brain git + candidate versioning  
- Owner-only tools stay in `OWNER_ONLY_TOOLS` where required  

## 6. APIs

| Endpoint | Role |
|---|---|
| `GET /self-evolve/status` | Authority map + metrics |
| `GET /self-evolve/experiences` | Recent experience events |
| `POST /self-evolve/experiences` | Record an event |
| `GET /self-evolve/metrics` | Daily counters |
| `POST /self-evolve/research` | Propose repo research |
| `POST /self-evolve/research/{id}/decide` | Approve/reject proposal (review only) |
| `GET /knowledge/stats` | Knowledge intel stats |
| `POST /knowledge/search` | Hybrid retrieve |
| `POST /knowledge/ingest` | Ingest with dedupe |

MCP tools: `javis_evolve`, `javis_knowledge` (plus existing `javis_memory`).

## 7. Environment

| Variable | Purpose |
|---|---|
| `BRAINS_DIR` | Persistent brains (required for learning durability) |
| Existing learn / improvement settings | Self-learning page switches |
| `FREE_LLM_PRESET` / model keys | Brains for analysis passes |
| Do **not** set auto-activation flags | Keep human approve |

## 8. Deployment

- **Vercel**: API + UI OK; do not run 24/7 improve workers there  
- **Local / Docker**: Enable Self-learning Write mode + optional improvement pilots  
- Persistent volume on `brains/`  

## 9. Tests

- `tests/test_self_evolve.py` — experience + research proposal  
- `tests/test_knowledge_intel.py` — ingest dedupe + search  

## 10. Known limitations

- Auto-activation of improvement candidates is intentionally **off**  
- No continuous model-weight training  
- Full RAGFlow/LlamaIndex stacks not embedded (avoid dual orchestrators)  
- Background research does not clone repos  

## 11. Roadmap

1. Hook tool-error paths to `self_evolve.record_experience` automatically  
2. Self-Improvement Center page that embeds existing candidates UI + experience feed  
3. Optional DeepEval/promptfoo CI job using sealed qualification cases  
4. Optional Graphiti sidecar for temporal edges  

## 12. Final objective check

AAROHI becomes more capable through **verified experience** (learn + improvement metrics + owner control), without compromising reliability, privacy, or replacing the working Self-learning / Improvement stack.
