"""HTTP surface for AAROHI Capability Studio (registry, repo inspect, plugin authoring)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import JSONResponse

import capability_studio
import localefmt
import plugin_authoring


@dataclass
class CapabilityStudioDeps:
    co_phien: Callable[[Request], bool]
    brain_root: Callable[[str], str]
    after_plugin_change: Callable[[str], None]


_DEPS: Optional[CapabilityStudioDeps] = None


def _deny():
    return JSONResponse(
        {"ok": False, "error": localefmt.chu(
            "Cần đăng nhập vào AAROHI để dùng Capability Studio.",
            "Sign in to AAROHI to use Capability Studio.")},
        status_code=401,
    )


def _make_router() -> APIRouter:
    router = APIRouter(prefix="/capability-studio", tags=["capability-studio"])

    @router.get("/registry")
    async def studio_registry(request: Request, brain: str = Query("brain")):
        if not _DEPS.co_phien(request):
            return _deny()
        root = _DEPS.brain_root(brain or "brain")
        return capability_studio.registry(root, brain_id=brain or "brain")

    @router.get("/services")
    async def studio_services(request: Request):
        if not _DEPS.co_phien(request):
            return _deny()
        return capability_studio.services_detail()

    @router.post("/repo/inspect")
    async def studio_repo_inspect(request: Request, url: str = Form(...)):
        if not _DEPS.co_phien(request):
            return _deny()
        return capability_studio.inspect_repository(url)

    @router.get("/plugins/files")
    async def studio_plugin_files(request: Request, slug: str = Query(...),
                                  brain: str = Query("brain"), scope: str = Query("")):
        if not _DEPS.co_phien(request):
            return _deny()
        try:
            return {"ok": True, **plugin_authoring.read_plugin(
                slug, _DEPS.brain_root(brain or "brain"), scope=scope or "")}
        except plugin_authoring.AuthoringError as e:
            return JSONResponse({"ok": False, "error": str(e)}, status_code=400)

    @router.post("/plugins/write")
    async def studio_plugin_write(request: Request, slug: str = Form(...),
                                  files_json: str = Form("{}"),
                                  scope: str = Form("global"),
                                  brain: str = Form("brain"),
                                  remove_json: str = Form("[]")):
        """Save candidate plugin files. Code/permission changes force enabled=false."""
        if not _DEPS.co_phien(request):
            return _deny()
        import json
        try:
            files = json.loads(files_json or "{}")
            remove = json.loads(remove_json or "[]")
        except ValueError:
            return JSONResponse({"ok": False, "error": "Invalid JSON for files/remove"}, status_code=400)
        try:
            res = plugin_authoring.write_plugin(
                slug, files, _DEPS.brain_root(brain or "brain"),
                scope=scope or "global", remove=remove)
            plugin_authoring.refresh_hub()
            _DEPS.after_plugin_change(brain or "brain")
            return res
        except plugin_authoring.AuthoringError as e:
            return JSONResponse({"ok": False, "error": str(e)}, status_code=400)

    @router.post("/plugins/restore")
    async def studio_plugin_restore(request: Request, slug: str = Form(...),
                                    scope: str = Form("global"),
                                    brain: str = Form("brain")):
        if not _DEPS.co_phien(request):
            return _deny()
        try:
            res = plugin_authoring.restore_backup(
                slug, _DEPS.brain_root(brain or "brain"), scope=scope or "global")
            plugin_authoring.refresh_hub()
            _DEPS.after_plugin_change(brain or "brain")
            return res
        except plugin_authoring.AuthoringError as e:
            return JSONResponse({"ok": False, "error": str(e)}, status_code=400)

    @router.get("/plugins/list-editable")
    async def studio_plugins_editable(request: Request, brain: str = Query("brain")):
        if not _DEPS.co_phien(request):
            return _deny()
        return {"ok": True, **plugin_authoring.list_plugins(_DEPS.brain_root(brain or "brain"))}

    return router


def register(app, deps: CapabilityStudioDeps) -> None:
    global _DEPS
    _DEPS = deps
    app.include_router(_make_router())
