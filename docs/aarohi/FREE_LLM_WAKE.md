# AAROHI free LLM wake-up

## What broke

OpenAI Compatible (LLM7) returned:

- `401 authentication_error` - saved/env API key invalid, expired, or revoked
- `429 insufficient_quota` - daily token window full

Chat stopped instead of hopping to another free brain.

## What AAROHI does now

1. **Anonymous first** - `OPENAI_COMPAT_KEY` empty, model `turbo`, base `https://api.llm7.io/v1`
2. **No fake Bearer** - anonymous requests omit the Authorization header
3. **On 401** - clear the bad key, rotate to the next anonymous endpoint (OVH), hop usage order
4. **On 429** - rest the route, rotate free endpoint when possible, hop to Groq/Gemini/OpenRouter if keyed
5. **Startup wake** - `universal_brain.wake_free_brain()` after `apply_model_env`

## Verified keyless endpoints (smoke-tested)

| Preset | Base URL | Model | Key |
|--------|----------|-------|-----|
| llm7 | `https://api.llm7.io/v1` | `turbo` | none |
| ovh-anonymous | `https://oai.endpoints.kepler.ai.cloud.ovh.net/v1` | `Meta-Llama-3_3-70B-Instruct` | none |

## Optional free keys (raise limits - you create them)

AAROHI never invents API keys. Get free-tier keys yourself:

- Groq: https://console.groq.com/keys
- Gemini: https://aistudio.google.com/app/apikey
- OpenRouter: https://openrouter.ai/keys (use `:free` models)
- LLM7 token (optional): https://token.llm7.io

Set in Vercel / `.env` (never commit):

```
FREE_LLM_PRESET=llm7
OPENAI_COMPAT_BASE=https://api.llm7.io/v1
OPENAI_COMPAT_KEY=
OPENAI_COMPAT_MODEL=turbo
GROQ_API_KEY=
GEMINI_API_KEY=
OPENROUTER_API_KEY=
OPENROUTER_MODEL=openrouter/free
```

## Manual wake

```
POST /universal-brain/wake
GET  /universal-brain/status
GET  /free-llm-presets
```

On Models page: OpenAI Compatible → clear the key field → model `turbo` → save.
