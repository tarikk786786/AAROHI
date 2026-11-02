"""Bundled plugin: clipboard get/set + short summarize hint for companion OS.

Enabled:false by default (user plugins safety). Uses pyperclip when available,
falls back to Windows clip.exe / PowerShell Get-Clipboard.
"""
from __future__ import annotations

import os
import subprocess
import sys
from typing import Optional

try:
    import deploy_info
except Exception:  # pragma: no cover
    deploy_info = None

try:
    import winproc
    _no_window = winproc.no_window
except Exception:  # pragma: no cover
    def _no_window():
        return getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0

IS_WIN = os.name == "nt"
DONE, ASK, FAILED = "[done]", "[ask]", "ERROR: [failed]"
_MAX = 8000


def check_ready() -> Optional[str]:
    mode = deploy_info.deploy_mode() if deploy_info else ("windows" if IS_WIN else "native")
    if mode == "docker":
        return (
            "Aarohi is in Docker on a server, so the host clipboard is not yours. "
            "Run Aarohi locally to use clipboard assist."
        )
    return None


def _get_clip() -> str:
    try:
        import pyperclip
        return str(pyperclip.paste() or "")
    except Exception:
        pass
    if IS_WIN:
        try:
            out = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command", "Get-Clipboard -Raw"],
                creationflags=_no_window(),
                stderr=subprocess.DEVNULL,
                timeout=8,
            )
            return out.decode("utf-8", errors="replace")
        except Exception as e:
            raise RuntimeError(str(e)) from e
    try:
        out = subprocess.check_output(["pbpaste"], stderr=subprocess.DEVNULL, timeout=5)
        return out.decode("utf-8", errors="replace")
    except Exception:
        out = subprocess.check_output(["xclip", "-selection", "clipboard", "-o"],
                                      stderr=subprocess.DEVNULL, timeout=5)
        return out.decode("utf-8", errors="replace")


def _set_clip(text: str) -> None:
    try:
        import pyperclip
        pyperclip.copy(text)
        return
    except Exception:
        pass
    if IS_WIN:
        p = subprocess.Popen(
            ["clip"],
            stdin=subprocess.PIPE,
            creationflags=_no_window(),
        )
        assert p.stdin is not None
        p.stdin.write(text.encode("utf-16le"))
        p.stdin.close()
        p.wait(timeout=5)
        return
    try:
        p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        assert p.stdin is not None
        p.stdin.write(text.encode("utf-8"))
        p.stdin.close()
        p.wait(timeout=5)
        return
    except Exception:
        p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
        assert p.stdin is not None
        p.stdin.write(text.encode("utf-8"))
        p.stdin.close()
        p.wait(timeout=5)


def _get(args, ctx) -> str:
    why = check_ready()
    if why:
        return f"{FAILED} {why}"
    try:
        text = _get_clip()
    except Exception as e:
        return f"{FAILED} cannot read clipboard: {e}"
    if not text.strip():
        return f"{DONE} Clipboard is empty."
    if len(text) > _MAX:
        return f"{DONE} Clipboard ({len(text)} chars, showing first {_MAX}):\n{text[:_MAX]}…"
    return f"{DONE} Clipboard ({len(text)} chars):\n{text}"


def _set(args, ctx) -> str:
    why = check_ready()
    if why:
        return f"{FAILED} {why}"
    text = str((args or {}).get("text") or "")
    if not text:
        return f"{ASK} Provide text to copy."
    if len(text) > _MAX:
        return f"{ASK} Text is {len(text)} chars; max {_MAX}."
    try:
        _set_clip(text)
    except Exception as e:
        return f"{FAILED} cannot write clipboard: {e}"
    return f"{DONE} Copied {len(text)} chars to clipboard."


def _summarize(args, ctx) -> str:
    """Return clipboard text with a short instruction for the model to summarize/translate in chat."""
    why = check_ready()
    if why:
        return f"{FAILED} {why}"
    mode = str((args or {}).get("mode") or "summarize").strip().lower()
    try:
        text = _get_clip()
    except Exception as e:
        return f"{FAILED} cannot read clipboard: {e}"
    if not text.strip():
        return f"{ASK} Clipboard is empty - nothing to {mode}."
    body = text if len(text) <= _MAX else text[:_MAX] + "…"
    if mode in ("translate", "hinglish", "hi"):
        hint = "Translate the clipboard text into warm Hinglish for the user."
    else:
        hint = "Summarize the clipboard text in 2-4 short sentences for the user."
    return f"{DONE} {hint}\n\n--- clipboard ---\n{body}"


def register(ctx):
    ctx.register_tool(
        name="javis_clipboard_get",
        description="Read the host clipboard text. Use when the user says paste/clipboard/what I copied.",
        handler=_get, min_mode="readonly", check_fn=check_ready,
        schema={"type": "object", "properties": {}},
    )
    ctx.register_tool(
        name="javis_clipboard_set",
        description="Write text to the host clipboard. text: string to copy.",
        handler=_set, min_mode="safe", check_fn=check_ready,
        schema={"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
    )
    ctx.register_tool(
        name="javis_clipboard_summarize",
        description=("Read clipboard and return it with a summarize/translate hint for the chat reply. "
                     "mode: summarize (default) or translate/hinglish."),
        handler=_summarize, min_mode="readonly", check_fn=check_ready,
        schema={"type": "object", "properties": {"mode": {"type": "string"}}},
    )
