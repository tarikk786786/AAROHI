"""Bundled plugin: screenshot + keyboard/mouse on the machine running Aarohi.

Clean original implementation for AAROHI. Complements desktop-apps (open/close/list).
Optional deps: pyautogui, Pillow. Missing deps return a clear install hint, not a crash.

Outcome prefixes match desktop-apps: [done] verified, [unverified] sent but unconfirmed,
[ask] refused as a guess, ERROR: [failed] could not run.
"""
from __future__ import annotations

import base64
import os
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

try:
    import deploy_info
except Exception:  # pragma: no cover
    deploy_info = None

IS_WIN = os.name == "nt"
IS_MAC = sys.platform == "darwin"

DONE, UNVERIFIED, ASK, FAILED = "[done]", "[unverified]", "[ask]", "ERROR: [failed]"
OUTCOME = (
    "Result starts with [done] (checked), [unverified] (sent, not confirmed), "
    "[ask] (refused - would guess), or ERROR: [failed]."
)

# Injected in tests
_capture_fn: Optional[Callable[[], Any]] = None
_type_fn: Optional[Callable[[str, float], None]] = None
_click_fn: Optional[Callable[[int, int, str, int], None]] = None
_hotkey_fn: Optional[Callable[[Tuple[str, ...]], None]] = None
_scroll_fn: Optional[Callable[[int, Optional[int], Optional[int]], None]] = None
_size_fn: Optional[Callable[[], Tuple[int, int]]] = None
_pos_fn: Optional[Callable[[], Tuple[int, int]]] = None

_MAX_SHOT_PX = 1920
_MAX_TYPE = 4000
_PROTECTED_HOTKEYS = {
    ("alt", "f4"), ("command", "q"), ("ctrl", "alt", "delete"),
    ("ctrl", "shift", "esc"), ("win", "l"), ("command", "option", "esc"),
}


def check_ready() -> Optional[str]:
    mode = deploy_info.deploy_mode() if deploy_info else ("windows" if IS_WIN else "native")
    if mode == "docker":
        return (
            "Aarohi is running in Docker on a server, not on your desktop, so she cannot "
            "control the screen you are looking at. Run Aarohi locally on this PC to use "
            "desktop control."
        )
    if not IS_WIN and not IS_MAC and not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        return "This Linux host has no display (no DISPLAY/WAYLAND_DISPLAY), so GUI control is unavailable."
    return None


def _need_gui() -> Optional[str]:
    why = check_ready()
    if why:
        return why
    try:
        import pyautogui  # noqa: F401
    except Exception:
        return (
            "Missing Python package pyautogui. Install with: pip install pyautogui pillow "
            "then restart Aarohi."
        )
    return None


def _gui():
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.05
    return pyautogui


def _screen_size() -> Tuple[int, int]:
    if _size_fn:
        return _size_fn()
    return tuple(_gui().size())  # type: ignore[return-value]


def _mouse_pos() -> Tuple[int, int]:
    if _pos_fn:
        return _pos_fn()
    return tuple(_gui().position())  # type: ignore[return-value]


def _capture_image():
    if _capture_fn:
        return _capture_fn()
    try:
        from PIL import ImageGrab
        return ImageGrab.grab(all_screens=False)
    except Exception:
        return _gui().screenshot()


def _shrink(img):
    w, h = img.size
    if max(w, h) <= _MAX_SHOT_PX:
        return img
    scale = _MAX_SHOT_PX / float(max(w, h))
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    return img.resize((nw, nh))


def _save_shot(ctx) -> Tuple[Optional[Path], str]:
    try:
        img = _capture_image()
    except Exception as e:
        return None, f"{FAILED} screenshot failed: {e}"
    try:
        img = _shrink(img)
    except Exception:
        pass
    folder = Path(getattr(ctx, "data_dir", None) or Path.cwd()) / "shots"
    try:
        folder.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return None, f"{FAILED} cannot write shot folder: {e}"
    path = folder / f"shot_{int(time.time())}.png"
    try:
        img.save(path, format="PNG")
    except Exception as e:
        return None, f"{FAILED} cannot save PNG: {e}"
    return path, ""


def _shot(args, ctx) -> str:
    miss = _need_gui()
    if miss:
        return f"{FAILED} {miss}"
    path, err = _save_shot(ctx)
    if err:
        return err
    assert path is not None
    w, h = _screen_size()
    mx, my = _mouse_pos()
    # Prefer a vault-relative path when the shot lands under the brain
    rel = str(path)
    try:
        vault = Path(getattr(ctx, "vault_root", "") or "")
        if vault and path.is_relative_to(vault):
            rel = path.relative_to(vault).as_posix()
    except Exception:
        pass
    # Small inline preview for chat engines that accept data URLs in tool results
    b64 = ""
    try:
        raw = path.read_bytes()
        if len(raw) <= 350_000:
            b64 = base64.b64encode(raw).decode("ascii")
    except Exception:
        pass
    preview = f" data:image/png;base64,{b64}" if b64 else ""
    return (
        f"{DONE} Screenshot saved to {rel}. Screen {w}x{h}, mouse at ({mx},{my})."
        f" Embed in chat as ![shot]({rel}) when the path is under the vault."
        f"{preview}"
    )


def _info(args, ctx) -> str:
    miss = _need_gui()
    if miss:
        return f"{FAILED} {miss}"
    try:
        w, h = _screen_size()
        mx, my = _mouse_pos()
    except Exception as e:
        return f"{FAILED} {e}"
    return f"{DONE} screen={w}x{h} mouse=({mx},{my}) platform={sys.platform}"


def _type_text(args, ctx) -> str:
    miss = _need_gui()
    if miss:
        return f"{FAILED} {miss}"
    text = str((args or {}).get("text") or "")
    if not text:
        return f"{ASK} Provide non-empty text to type."
    if len(text) > _MAX_TYPE:
        return f"{ASK} Text is {len(text)} chars; max {_MAX_TYPE}. Split into shorter calls."
    interval = float((args or {}).get("interval") or 0.02)
    interval = max(0.0, min(interval, 0.2))
    try:
        if _type_fn:
            _type_fn(text, interval)
        else:
            _gui().write(text, interval=interval)
    except Exception as e:
        return f"{FAILED} type failed: {e}"
    return f"{UNVERIFIED} Typed {len(text)} characters into the focused window (not read back)."


def _parse_xy(args: Dict[str, Any]) -> Tuple[Optional[int], Optional[int], str]:
    if "x" not in args or "y" not in args:
        return None, None, "x and y are required (screen pixels, origin top-left)."
    try:
        x, y = int(args["x"]), int(args["y"])
    except (TypeError, ValueError):
        return None, None, "x and y must be integers."
    w, h = _screen_size()
    if x < 0 or y < 0 or x >= w or y >= h:
        return None, None, f"({x},{y}) is outside the screen {w}x{h}."
    return x, y, ""


def _click(args, ctx) -> str:
    miss = _need_gui()
    if miss:
        return f"{FAILED} {miss}"
    args = args or {}
    x, y, why = _parse_xy(args)
    if why:
        return f"{ASK} {why}"
    button = str(args.get("button") or "left").lower()
    if button not in ("left", "right", "middle"):
        return f"{ASK} button must be left, right, or middle."
    try:
        clicks = int(args.get("clicks") or 1)
    except (TypeError, ValueError):
        return f"{ASK} clicks must be an integer."
    clicks = max(1, min(clicks, 3))
    try:
        if _click_fn:
            _click_fn(x, y, button, clicks)  # type: ignore[arg-type]
        else:
            _gui().click(x=x, y=y, clicks=clicks, button=button)
    except Exception as e:
        return f"{FAILED} click failed: {e}"
    return f"{UNVERIFIED} Clicked {button} x{clicks} at ({x},{y})."


def _norm_keys(keys) -> Tuple[str, ...]:
    if isinstance(keys, str):
        parts = [p.strip().lower() for p in keys.replace("+", " ").split() if p.strip()]
    elif isinstance(keys, (list, tuple)):
        parts = [str(p).strip().lower() for p in keys if str(p).strip()]
    else:
        parts = []
    aliases = {"control": "ctrl", "ctl": "ctrl", "cmd": "command", "opt": "option", "windows": "win"}
    return tuple(aliases.get(p, p) for p in parts)


def _hotkey(args, ctx) -> str:
    miss = _need_gui()
    if miss:
        return f"{FAILED} {miss}"
    keys = _norm_keys((args or {}).get("keys"))
    if len(keys) < 1:
        return f"{ASK} keys required, e.g. 'ctrl c' or ['ctrl','v']."
    if keys in _PROTECTED_HOTKEYS or tuple(sorted(keys)) in {tuple(sorted(k)) for k in _PROTECTED_HOTKEYS}:
        return f"{ASK} Refused protected hotkey {'+'.join(keys)} (logout / force-quit / task manager)."
    try:
        if _hotkey_fn:
            _hotkey_fn(keys)
        else:
            _gui().hotkey(*keys)
    except Exception as e:
        return f"{FAILED} hotkey failed: {e}"
    return f"{UNVERIFIED} Sent hotkey {'+'.join(keys)}."


def _scroll(args, ctx) -> str:
    miss = _need_gui()
    if miss:
        return f"{FAILED} {miss}"
    args = args or {}
    try:
        amount = int(args.get("amount") or 0)
    except (TypeError, ValueError):
        return f"{ASK} amount must be an integer (positive=up, negative=down)."
    if amount == 0:
        return f"{ASK} amount cannot be 0."
    amount = max(-50, min(50, amount))
    x = args.get("x")
    y = args.get("y")
    ix = iy = None
    if x is not None or y is not None:
        ix, iy, why = _parse_xy({"x": x if x is not None else _mouse_pos()[0],
                                 "y": y if y is not None else _mouse_pos()[1]})
        if why:
            return f"{ASK} {why}"
    try:
        if _scroll_fn:
            _scroll_fn(amount, ix, iy)
        else:
            g = _gui()
            if ix is not None and iy is not None:
                g.scroll(amount, x=ix, y=iy)
            else:
                g.scroll(amount)
    except Exception as e:
        return f"{FAILED} scroll failed: {e}"
    where = f" at ({ix},{iy})" if ix is not None else ""
    return f"{UNVERIFIED} Scrolled {amount} notches{where}."


def register(ctx):
    ctx.register_tool(
        name="javis_screen_info",
        description=("Screen size and mouse position on the machine running Aarohi. "
                     "Call before click/type when you need coordinates. " + OUTCOME),
        handler=_info, min_mode="readonly", check_fn=check_ready,
        schema={"type": "object", "properties": {}},
    )
    ctx.register_tool(
        name="javis_screen_shot",
        description=("Capture the primary screen to a PNG under the plugin data folder and return "
                     "its path. Use when the user asks what is on screen, or before clicking UI. "
                     + OUTCOME),
        handler=_shot, min_mode="safe", check_fn=check_ready,
        schema={"type": "object", "properties": {}},
    )
    ctx.register_tool(
        name="javis_type_text",
        description=("Type unicode text into the focused window (like a keyboard). "
                     "Focus the target app first with javis_app_open. text: string. "
                     "interval: seconds between keys (default 0.02). " + OUTCOME),
        handler=_type_text, min_mode="full", check_fn=check_ready,
        schema={"type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "interval": {"type": "number"},
                },
                "required": ["text"]},
    )
    ctx.register_tool(
        name="javis_click",
        description=("Click at screen pixel (x,y), origin top-left. button: left|right|middle. "
                     "clicks: 1-3. Get size via javis_screen_info or javis_screen_shot first. "
                     + OUTCOME),
        handler=_click, min_mode="full", check_fn=check_ready,
        schema={"type": "object",
                "properties": {
                    "x": {"type": "integer"},
                    "y": {"type": "integer"},
                    "button": {"type": "string"},
                    "clicks": {"type": "integer"},
                },
                "required": ["x", "y"]},
    )
    ctx.register_tool(
        name="javis_hotkey",
        description=("Press a modifier combo, e.g. keys='ctrl c' or keys=['ctrl','v']. "
                     "Refuses force-quit / lock-screen combos. " + OUTCOME),
        handler=_hotkey, min_mode="full", check_fn=check_ready,
        schema={"type": "object",
                "properties": {
                    "keys": {"description": "Space/+ string or array of key names",
                             "oneOf": [{"type": "string"},
                                       {"type": "array", "items": {"type": "string"}}]},
                },
                "required": ["keys"]},
    )
    ctx.register_tool(
        name="javis_scroll",
        description=("Scroll the wheel. amount: positive=up, negative=down, clamped ±50. "
                     "Optional x,y to move mouse first. " + OUTCOME),
        handler=_scroll, min_mode="full", check_fn=check_ready,
        schema={"type": "object",
                "properties": {
                    "amount": {"type": "integer"},
                    "x": {"type": "integer"},
                    "y": {"type": "integer"},
                },
                "required": ["amount"]},
    )
