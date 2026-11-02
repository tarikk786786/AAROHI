"""AAROHI girlfriend voice stack status (no heavy model download).

    python tests/run.py aarohi_girlfriend_voice
"""
from _paths import SERVER  # noqa: F401
import importlib
import os
import sys

sys.path.insert(0, str(SERVER))
_fails = []


def check(name, cond):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        _fails.append(name)


# Indic-Speak module loads and reports status without crashing when deps missing
tis = importlib.import_module("tts_indic_speak")
st = tis.status()
check("indic status keys", st.get("speaker") == "Kavya" and st.get("provider") == "indic_speak")
check("indic not required", "available" in st)

# Shruti module status
ss = importlib.import_module("stt_shruti")
sh = ss.status()
check("shruti status keys", sh.get("provider") == "shruti" and "available" in sh)

# Ear ranking knows shruti
ve = importlib.import_module("voice_ear")
check("shruti in CHOICES", "shruti" in ve.CHOICES)
check("shruti in EARS", "shruti" in ve.EARS)
check("ranking has shruti", "shruti" in ve.RANKING)

# Hotwords include Aarohi
ns = importlib.import_module("nghe_sua")
check("aarohi in vocab root", "Aarohi" in ns.TU_VUNG_GOC)

# Voice brain prompt is girlfriend-coded
vb = importlib.import_module("voice_brain")
check("prompt names Aarohi", "Aarohi" in vb.SYSTEM_PROMPT and "girlfriend" in vb.SYSTEM_PROMPT.lower())
check("prompt Hinglish", "Hinglish" in vb.SYSTEM_PROMPT or "Hinglish" in vb.SYSTEM_PROMPT)

print()
if _fails:
    print("FAILED:", ", ".join(_fails))
    raise SystemExit(1)
print("all ok")
