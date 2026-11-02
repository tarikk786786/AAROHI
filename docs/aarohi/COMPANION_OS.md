# AAROHI Companion OS (Mark-capability, clean-room)

Web-first companion on the existing Javis server. **Do not clone** [FatihMakes/Mark-LVI](https://github.com/FatihMakes/Mark-LVI) (CC BY-NC). Patterns only; all code here is original AAROHI/Javis.

## One-click Windows

1. Double-click `AAROHI-setup.bat` (wraps `install.ps1`).
2. Installs venv deps, optional `pyautogui` + `pillow`, pins Hinglish Swara @ −8%, creates Desktop `AAROHI.lnk`, starts server.
3. Open `http://127.0.0.1:7777/`. Daily start: `AAROHI-start.bat` (alias `start-javis.bat`).

## Any-device remote

- First-run wizard step **Open AAROHI from your phone** starts a Cloudflare quick tunnel (`/remote-access/enable`, mode=quick).
- Or Settings → Remote access (same `remote_tunnel.py` supervisor).
- **Login password is required** while the tunnel is on.
- **Mic needs HTTPS** - the tunnel URL is `https://…trycloudflare.com`, which satisfies browser mic policy. Plain `http://LAN-IP:7777` from a phone often cannot open the mic.

## Desktop control

Runs only on the Windows host that runs `server/main.py`. Phones drive that host through the authenticated dashboard + tunnel.

- `desktop-apps`: list / open / **raise** / close (`force` needs `confirm=true`)
- `desktop-control`: screenshot / type / click / hotkey / scroll
- Both refuse Docker hosts with a clear message.

## Voice (basic call path)

- Hold **Space** (outside inputs) or hold the mic button for push-to-talk (`companion-voice.js`).
- Self-echo guard drops STT that matches the last TTS line.
- Instant short Hinglish ack when a long tool/status turn starts.

## Clipboard (optional)

`system/plugins/clipboard-assist` ships `enabled: false`. Enable in the app Plugins page when you want get/set/summarize clipboard tools.
