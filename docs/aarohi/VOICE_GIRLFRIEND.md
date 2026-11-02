# Aarohi girlfriend voice (Hinglish)

Goal: soft Indian caring romantic girlfriend - sound + persona.

## Voice ladder (TTS)

| Priority | Engine | Voice | When |
|----------|--------|-------|------|
| 1 | **Indic-Speak** (Bodhan AI) | **Kavya** | Optional local (~6.6 GB, gated HF). Best natural Hindi/English mix. |
| 2 | Edge TTS (free) | **hi-IN-SwaraNeural** at **−8%** | Always-on default. Sweet Hindi girl. |
| 3 | Edge / OpenAI / ElevenLabs | Neerja, shimmer, etc. | Manual pick in Settings. |

Alternatives for experiments (not wired as required deps): IndicF5, Hinglish-TTS, DhVaani.

## Hearing (STT)

| Priority | Ear | Notes |
|----------|-----|-------|
| 1 | Groq Whisper | If API key set (`voice.ear=auto`) |
| 2 | **Shruti** | Offline Hindi/English/Hinglish, ~29.5 MB, Apache-2.0 |
| 3 | OpenAI gpt-4o-transcribe | If OpenAI key set |
| 4 | Browser Web Speech | Fallback |

## Install optional stack (Windows)

1. Accept [bodhan-ai/indic-speak](https://huggingface.co/bodhan-ai/indic-speak) terms; set `HF_TOKEN`.
2. Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install-aarohi-voice.ps1
```

3. Restart Aarohi. Settings → Voice should show **Kavya · Indic-Speak**. Ear auto can pick Shruti when cactus-needle is installed.

## License notes

- Indic-Speak: Bodhan terms (attribution; ask before hosting as a public API for others).
- Shruti: Apache-2.0 (Udgam Labs / Cactus Whistle).
- Do not vendor Mark-LVI or other CC BY-NC sources for voice.
