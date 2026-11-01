# AAROHI Universal API Hub

Central **index** of API collections, SDKs, MCP connectors and self-hostable services for Aarohi’s agentic OS.

This is **not** an instruction to install every repository. AAROHI already owns orchestration (`main` + engines), tools (`mcp_hub`), brains (Models + `openai-compat`), channels, vault, and voice.

Source of truth file: [`system/api-hub-registry.json`](../../system/api-hub-registry.json)  
Live JSON: `GET /api-hub/registry`

## Audit snapshot (existing project)

| Capability | Already in AAROHI | Do not replace with |
|---|---|---|
| Tool protocol | MCP Hub + Connections | LangChain / Agno as core |
| Multi-LLM | OpenRouter, Groq, Gemini, openai-compat, Ollama local | Portkey unless you need it |
| Free cloud brain | `FREE_LLM_PRESET=llm7` → openai-compat | Paid-only gateways |
| Channels | Telegram, Discord, Slack, Zalo, WhatsApp | Rewriting bots |
| Voice | Edge TTS (default **hi-IN-SwaraNeural** sweet Hindi girlfriend) | Heavy local TTS stacks on Vercel |
| Memory | Brain vault + settings | Forced Supabase |
| Auth | Built-in dashboard auth | Keycloak (overkill for personal OS) |

## How to use a catalog entry

1. Prefer **Connections → MCP** if an MCP server exists.
2. Prefer **Models → OpenAI Compatible** for any OpenAI `/v1` gateway (LiteLLM, vLLM, LLM7, Aion…).
3. Prefer a **skill/plugin** for one-off Python tools (yfinance, GeoPy, OCR).
4. Prefer a **sidecar** (n8n, Pipedream) for heavy workflows — do not embed in Vercel serverless.
5. Check **license, rate limits, free-tier terms** before marking anything “free”.

## Priority stack (phase order)

1. This registry + discovery docs  
2. OpenAPI directory / Jentic (specs for future tool gen)  
3. LiteLLM **optional** behind openai-compat  
4. Composio / OpenConnector only for MCP gaps  
5. MCP SDK — **already adopted**  
6. n8n — optional sidecar  
7. Supabase — optional if vault is not enough  
8. Infisical / env secrets  
9. Prometheus/Grafana — ops only  
10. Hurl / Insomnia — developer testing  

## India-focused notes

- Portals: [data.gov.in](https://www.data.gov.in/), [API Setu](https://apisetu.gov.in/), NPCI, UIDAI (official only).  
- Payments SDKs (Razorpay, PhonePe) need merchant credentials — never commit keys.  
- Girlfriend persona + Hindi voice are product UX; India APIs are separate connectors.

## Free LLM brains (related)

See also:

- [`system/free-llm-presets.json`](../../system/free-llm-presets.json)  
- [`docs/en/free-llm-apis.md`](./free-llm-apis.md)  
- [`docs/en/free-llm-collection-repos.md`](./free-llm-collection-repos.md)

On Vercel, with no Claude/Codex CLI, AAROHI auto-seeds **LLM7** as MAIN via `openai-compat` so chat is never stuck on “No AI model connected”.

## Voice defaults (Aarohi)

| Setting | Value |
|---|---|
| Edge voice | `hi-IN-SwaraNeural` (sweet Hindi girlfriend) |
| Hinglish/English-leaning | `en-IN-NeerjaNeural` |
| Rate | `-5%` (softer) |
| Env | `TTS_VOICE`, `TTS_RATE` |

## What was rejected for core install

- LangChain / Agno as primary orchestrator (duplicate authority)  
- Kong/Keycloak inside the girlfriend app  
- Cloning entire `public-apis` into the runtime  
- Paid SaaS as silent fallbacks  

## Next phases

See `phases` in `api-hub-registry.json`. Next useful code: Connections UI badges linking top MCP servers from this registry; optional OpenAPI→MCP generator behind a feature flag.
