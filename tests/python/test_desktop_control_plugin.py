"""Plugin desktop-control: screenshot / type / click / hotkey / scroll.

    python tests/run.py desktop_control

No real GUI: backends are faked. Locks:
  1. Docker deploy -> check_ready blocks.
  2. Missing coords / empty text / protected hotkeys -> [ask].
  3. Fake backends -> [done] or [unverified] with recorded calls.
  4. Manifest: six tools, modes readonly/safe/full.
"""
from _paths import ROOT, SERVER  # noqa: E402,F401
import importlib.util
import os
import tempfile
from pathlib import Path

os.environ["JAVIS_STATE_DIR"] = tempfile.mkdtemp(prefix="javis-dctl-")

import deploy_info  # noqa: E402
import yaml  # noqa: E402

_fails = []


def check(name, cond):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        _fails.append(name)


spec = importlib.util.spec_from_file_location(
    "desktop_control_plugin", ROOT / "system" / "plugins" / "desktop-control" / "plugin.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

calls = {"type": [], "click": [], "hotkey": [], "scroll": []}


class FakeImg:
    size = (800, 600)

    def resize(self, wh):
        self.size = wh
        return self

    def save(self, path, format=None):
        Path(path).write_bytes(b"\x89PNG\r\n\x1a\n" + b"\0" * 32)


m._capture_fn = lambda: FakeImg()
m._size_fn = lambda: (1920, 1080)
m._pos_fn = lambda: (100, 200)
m._type_fn = lambda text, interval: calls["type"].append((text, interval))
m._click_fn = lambda x, y, button, clicks: calls["click"].append((x, y, button, clicks))
m._hotkey_fn = lambda keys: calls["hotkey"].append(keys)
m._scroll_fn = lambda amount, x, y: calls["scroll"].append((amount, x, y))

# Pretend pyautogui is present when check_ready path needs it
import types
import sys as _sys
_sys.modules.setdefault("pyautogui", types.SimpleNamespace(
    FAILSAFE=True, PAUSE=0.05, size=lambda: (1920, 1080), position=lambda: (100, 200),
    write=lambda *a, **k: None, click=lambda *a, **k: None, hotkey=lambda *a, **k: None,
    scroll=lambda *a, **k: None, screenshot=lambda: FakeImg(),
))


class Ctx:
    def __init__(self):
        self.data_dir = Path(tempfile.mkdtemp(prefix="dctl-data-"))
        self.vault_root = self.data_dir


ctx = Ctx()

# ---- Docker block ----
_orig = deploy_info.deploy_mode
deploy_info.deploy_mode = lambda: "docker"
check("docker blocks", m.check_ready() is not None and "Docker" in m.check_ready())
deploy_info.deploy_mode = lambda: "windows"
check("native ready", m.check_ready() is None)
deploy_info.deploy_mode = _orig

# ---- info / shot ----
m.deploy_info = types.SimpleNamespace(deploy_mode=lambda: "windows")
info = m._info({}, ctx)
check("info done", info.startswith("[done]") and "1920x1080" in info)

shot = m._shot({}, ctx)
check("shot done", shot.startswith("[done]") and "Screenshot saved" in shot)
check("shot file exists", any(ctx.data_dir.joinpath("shots").glob("*.png")))

# ---- type / click / hotkey / scroll ----
check("empty type ask", m._type_text({"text": ""}, ctx).startswith("[ask]"))
t = m._type_text({"text": "hello", "interval": 0.01}, ctx)
check("type unverified", t.startswith("[unverified]") and calls["type"][-1][0] == "hello")

check("click missing ask", m._click({}, ctx).startswith("[ask]"))
check("click OOB ask", m._click({"x": 99999, "y": 1}, ctx).startswith("[ask]"))
c = m._click({"x": 10, "y": 20, "button": "left", "clicks": 2}, ctx)
check("click ok", c.startswith("[unverified]") and calls["click"][-1] == (10, 20, "left", 2))

check("hotkey protected", m._hotkey({"keys": "alt+f4"}, ctx).startswith("[ask]"))
h = m._hotkey({"keys": ["ctrl", "c"]}, ctx)
check("hotkey ok", h.startswith("[unverified]") and calls["hotkey"][-1] == ("ctrl", "c"))

s = m._scroll({"amount": -3}, ctx)
check("scroll ok", s.startswith("[unverified]") and calls["scroll"][-1][0] == -3)

# ---- manifest ----
man = yaml.safe_load((ROOT / "system" / "plugins" / "desktop-control" / "plugin.yaml").read_text(encoding="utf-8"))
check("slug", man["slug"] == "desktop-control")
check("enabled", man["enabled"] is True)
check("six tools", len(man["tools"]) == 6)
check("min_mode safe", man["min_mode"] == "safe")

print()
if _fails:
    print("FAILED:", ", ".join(_fails))
    raise SystemExit(1)
print("all ok")
