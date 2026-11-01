# Free LLM APIs for AAROHI

Source list: [mnfst/awesome-free-llm-apis](https://github.com/mnfst/awesome-free-llm-apis)

Machine-readable presets: [`system/free-llm-presets.json`](../../system/free-llm-presets.json)

## Fast path (built-in Models cards)

| Provider | Get key | Env var |
|----------|---------|---------|
| Groq | https://console.groq.com/keys | `GROQ_API_KEY` |
| Google Gemini | https://aistudio.google.com/app/apikey | `GEMINI_API_KEY` |
| OpenRouter | https://openrouter.ai/keys | `OPENROUTER_API_KEY` |

On Vercel: Project → Settings → Environment Variables → add the key → Redeploy.

## OpenAI Compatible presets

In **Models**, open **OpenAI Compatible**, paste base URL + key from the preset file.

Examples:

- **LLM7** (often works with empty key): `https://api.llm7.io/v1`
- **Aion Labs** (roleplay): `https://api.aionlabs.ai/v1`
- **Mistral free mode**: `https://api.mistral.ai/v1`
- **Zhipu GLM Flash**: `https://open.bigmodel.cn/api/paas/v4`

Or set env:

```powershell
$env:FREE_LLM_PRESET="llm7"
# optional token from https://token.llm7.io
$env:OPENAI_COMPAT_KEY="..."
```

## Ollama

`Could not connect. Is Ollama running…` means AAROHI cannot reach `http://127.0.0.1:11434`.

1. Install: `winget install Ollama.Ollama`
2. Start Ollama from the Start menu
3. In Models → Ollama local, endpoint `http://127.0.0.1:11434`

**Important:** The hosted site on Vercel cannot talk to Ollama on your laptop. For cloud AAROHI, use Groq / Gemini / OpenRouter / LLM7 instead. Use Ollama when running AAROHI locally.