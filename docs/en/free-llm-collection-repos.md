# Free LLM collection repos for AAROHI’s multi-brain

Use this as the research library for a **modular multi-LLM brain** (not one locked provider).  
Also see: [free-llm-apis.md](./free-llm-apis.md) · [system/free-llm-presets.json](../../system/free-llm-presets.json) · [mnfst/awesome-free-llm-apis](https://github.com/mnfst/awesome-free-llm-apis)

**Rule:** open-weight ≠ always free for commercial use. Check licenses. Local GPUs still cost power/hardware.

---

## 1. Best collection / runtime repos (add first)

| Repository | URL | Role in AAROHI |
|------------|-----|----------------|
| Awesome Free LLM APIs | https://github.com/mnfst/awesome-free-llm-apis | Free cloud API keys (OpenAI-compatible) |
| Awesome Local LLM | https://github.com/janhq/awesome-local-ai (and similar “awesome-local-llm” lists) | Local tools map |
| Awesome LLM | https://github.com/Hannibal046/Awesome-LLM | Papers, models, resources |
| Hugging Face Transformers | https://github.com/huggingface/transformers | Load pretrained models |
| Hugging Face Hub | https://huggingface.co/models | Searchable model catalogue |
| Open LLM Leaderboard | https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard | Compare quality |
| Ollama | https://github.com/ollama/ollama | Local model download + run |
| llama.cpp | https://github.com/ggerganov/llama.cpp | Quantized CPU/GPU local run |
| vLLM | https://github.com/vllm-project/vllm | High-throughput serving |
| SGLang | https://github.com/sgl-project/sglang | Fast inference |
| LocalAI | https://github.com/mudler/LocalAI | Self-hosted multi-model API |
| GPT4All | https://github.com/nomic-ai/gpt4all | Easy local desktop LLMs |
| LiteLLM | https://github.com/BerriAI/litellm | Unified router (local + API) |
| OpenRouter | https://openrouter.ai | Multi-provider API; free pool models |

---

## 2. Main model family collections

| Family | Repo | Best for |
|--------|------|----------|
| **Qwen** (priority) | https://github.com/QwenLM | Reasoning, coding, multilingual, VL/audio |
| **DeepSeek** | https://github.com/deepseek-ai | Hard reasoning, math, coding |
| **Llama** | https://github.com/meta-llama | General, tools, agents, fine-tunes |
| **Gemma** | https://github.com/google-gemma | Light local + vision |
| **Mistral** | https://github.com/mistralai | Efficient general + coding |
| **Phi** | https://github.com/microsoft/phi | Small SLMs, local |
| **OLMo** | https://github.com/allenai/OLMo | Fully open research models |
| **Nous / Hermes** | https://github.com/NousResearch | Strong instruction fine-tunes |

---

## 3. Coding brains

| Repo | URL |
|------|-----|
| Qwen Code / Qwen2.5-Coder | https://github.com/QwenLM |
| DeepSeek-Coder | https://github.com/deepseek-ai/DeepSeek-Coder |
| StarCoder2 | https://github.com/bigcode-project/starcoder2 |
| CodeGemma | https://huggingface.co/collections/google/codegemma-release |
| LlamaFactory (fine-tune) | https://github.com/hiyouga/LLaMA-Factory |
| Unsloth (efficient fine-tune) | https://github.com/unslothai/unsloth |

---

## 4. Agents / research orchestration

| Repo | URL | Role |
|------|-----|------|
| smolagents | https://github.com/huggingface/smolagents | Light agents |
| LangGraph | https://github.com/langchain-ai/langgraph | Stateful workflows |
| Qwen-Agent | https://github.com/QwenLM/Qwen-Agent | Tools + RAG |
| DSPy | https://github.com/stanfordnlp/dspy | Optimize pipelines |
| LlamaIndex | https://github.com/run-llama/llama_index | Knowledge retrieval |
| Haystack | https://github.com/deepset-ai/haystack | RAG / research |
| AutoGen | https://github.com/microsoft/autogen | Multi-agent |
| CrewAI | https://github.com/crewAIInc/crewAI | Role teams |

---

## 5. Memory & knowledge

| Repo | URL |
|------|-----|
| Mem0 | https://github.com/mem0ai/mem0 |
| Letta | https://github.com/letta-ai/letta |
| Graphiti | https://github.com/getzep/graphiti |
| Microsoft GraphRAG | https://github.com/microsoft/graphrag |
| Cognee | https://github.com/topoteretes/cognee |
| Chroma | https://github.com/chroma-core/chroma |
| Qdrant | https://github.com/qdrant/qdrant |
| FAISS | https://github.com/facebookresearch/faiss |
| Awesome AI Memory | search GitHub: `awesome-ai-memory` |

---

## 6. Embeddings / RAG docs

| Repo | URL |
|------|-----|
| Sentence Transformers | https://github.com/UKPLab/sentence-transformers |
| FlagEmbedding (BGE) | https://github.com/FlagOpen/FlagEmbedding |
| E5 | https://huggingface.co/intfloat |
| ColBERT | https://github.com/stanford-futuredata/ColBERT |
| RAGFlow | https://github.com/infiniflow/ragflow |
| Docling | https://github.com/DS4SD/docling |
| Awesome RAG | https://github.com/awesome-rag/awesome-rag (and forks) |

---

## 7. Vision / voice / multimodal

| Repo | URL | Role |
|------|-----|------|
| Qwen2/3-VL | https://github.com/QwenLM | Image / video |
| Qwen-Omni / audio variants | https://github.com/QwenLM | Multimodal |
| Whisper | https://github.com/openai/whisper | STT |
| Faster-Whisper | https://github.com/SYSTRAN/faster-whisper | Fast STT |
| Piper | https://github.com/rhasspy/piper | Local TTS |
| Kokoro | https://github.com/hexgrad/kokoro | Light TTS |
| Sherpa-ONNX | https://github.com/k2-fsa/sherpa-onnx | Offline speech |

*(AAROHI already uses Edge TTS / OpenAI TTS / Gemini Live — keep those; add local Piper/Whisper only for offline.)*

---

## 8. Recommended AAROHI mapping (do not install everything)

| Brain slot | First choice | Fallback |
|------------|--------------|----------|
| Main / reasoning | OpenRouter free / Qwen / DeepSeek API | Groq / Gemini free |
| Coding | DeepSeek / Qwen Coder via OpenRouter | Claude Code when signed in |
| Research | Gemini / Qwen + web tools | OpenRouter |
| Fast | Groq / small Ollama | LLM7 free |
| Local | Ollama + Qwen/Gemma/Phi | llama.cpp |
| Vision | Gemini / Qwen-VL APIs | — |
| Voice | Existing Edge Ava + Whisper later | Piper local |
| Memory | Keep AAROHI vault + Mem0 later | — |
| Router | Built-in Models order + LiteLLM later | OpenRouter |

**Hardware note (your PC unknown):** with ≤16 GB RAM and no strong NVIDIA GPU, prefer **API free tiers + small Ollama models (≤8B)**. Avoid 70B local until you confirm VRAM.

---

## 9. What AAROHI already supports today

- Claude Code, ChatGPT/Codex, OpenRouter, Groq, Gemini, DeepSeek, Ollama local, OpenAI Compatible  
- Usage order = MAIN + fallbacks when quota/deny  
- Presets: `system/free-llm-presets.json`  
- Env: `OPENROUTER_API_KEY`, `GROQ_API_KEY`, `GEMINI_API_KEY`, `FREE_LLM_PRESET=llm7`

Next incremental step (not a big-bang install): wire one free cloud brain (Groq or OpenRouter) + keep Ollama for local Fast Brain only.
