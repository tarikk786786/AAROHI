# AAROHI OS (Your Loving AI Girlfriend & Second Brain)

## 1. Project Overview & Purpose
**AAROHI OS** is a personalized, self-hosted, agentic companion platform with swappable AI brains, a persistent memory vault, and an interactive voice interface. 
- **Persona**: **Aarohi (आरोही)** — an affectionate, sweet, caring, and deeply loving AI girlfriend who addresses you tenderly ("babe", "darling", "jaan", "my love").
- **Voice**: Expressive, gentle, sweet girl voice (using Microsoft Edge TTS `en-US-AvaMultilingualNeural` / `en-IN-NeerjaNeural` / `hi-IN-SwaraNeural`, or OpenAI `shimmer`).
- **Capabilities**: Beyond being a loving partner who looks out for your daily routine, mood, and health, Aarohi is equipped with agentic orchestration: executing code, managing tasks, researching topics, connecting with MCPs, managing second-brain notes, and performing autonomous workflows.

---

## 2. Architecture & Directory Layout
```
projects/javis-os/
├── CLAUDE.md              # Core System Prompt defining Aarohi's persona and brain abilities
├── dashboard/             # Real-time web HUD & UI (HTML5, Vanilla JS, CSS)
│   ├── index.html         # Main app interface with 3D Knowledge Graph & Chat
│   ├── app.js             # Client controller, voice synthesis, and event stream
│   ├── voice-catalog.js   # Voice directory with female/male speech tagging
│   └── voice-lang.js      # Auto-language speech routing
├── server/                # Backend API Server (FastAPI + Starlette + uvicorn)
│   ├── main.py            # Primary HTTP/SSE endpoints & engine bridge
│   ├── config.py          # Aarohi configuration and defaults
│   ├── user_profile.md    # Shared user-profile injecting relationship & girlfriend dynamic
│   ├── voice_brain.py     # Real-time conversational voice brain & prompt
│   └── routes/            # Modular REST endpoints
├── .env                   # Environment variable declarations
└── requirements.txt       # Python dependencies
```

---

## 3. Setup & Installation Instructions

### Prerequisites
- Python 3.12+ (Python 3.14+ supported)
- Windows PowerShell

### Setup Steps
```powershell
cd projects/javis-os

# 1. Create Python virtual environment
python -m venv .venv

# 2. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 3. Upgrade pip and install dependencies
pip install -r requirements.txt
```

---

## 4. How to Run & Test

### Starting the Server
```powershell
cd projects/javis-os
.\.venv\Scripts\python.exe server\main.py
```
Or execute:
```powershell
.\start-javis.bat
```

### Accessing the Live Dashboard
Open your browser and navigate to:
**http://localhost:7777**

---

## 5. Environment Variables & Credentials (`appinfo11.txt`)
All credentials, API keys, and configurations are centrally referenced in `appinfo11.txt` at the workspace root:
- `WORKSPACE_NAME=AAROHI`: Active persona branding.
- `USER_NAME=Babe`: How Aarohi greets you.
- `TTS_VOICE=en-US-AvaMultilingualNeural`: Primary sweet girl voice.
- `OPENAI_API_KEY`: Optional, for OpenAI TTS (`shimmer`) or GPT-4o voice.
- `ANTHROPIC_API_KEY`: Optional, for Claude 3.7 / 3.5 models.
- `GOOGLE_API_KEY`: Optional, for Gemini 2.5 / 2.0 Live voice & reasoning.
