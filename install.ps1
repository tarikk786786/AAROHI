# ============================================================
# AAROHI Companion - one-shot Windows setup
#
#   powershell -ExecutionPolicy Bypass -File install.ps1
#   Or double-click AAROHI-setup.bat
#
# Installs Python deps (venv) + optional desktop control + four CLI brains
# (claude, codex, agy, grok) + .env + frees port 7777, then starts the server.
#
# Vi sao co file nay: truoc day nguoi dung Windows phai tu di bon duong khac nhau (setup.bat
# chi cai claude + codex; agy va grok phai tu mo PowerShell go tung lenh cua nha cung cap),
# nen ai khong quen ky thuat thi dung o man Models voi hai the bao "CLI chua cai".
#
# HAI CHO DE SAI, ca hai da xu ly trong file nay:
#   1. `pip install` HONG ma khong ai kiem ma loi -> server bat len roi moi chet vi thieu
#      claude-agent-sdk. Buoc [2] duoi day dung han va noi ro neu pip hong.
#   2. Cai CLI xong ma PATH cua PHIEN HIEN TAI chua co -> buoc tong ket bao "chua cai" cho
#      mot CLI vua cai xong. Refresh-Path doc lai PATH tu registry sau moi lan cai.
#
# QUAN TRONG: Javis doc PATH LUC NO BAT. Cai them CLI sau khi server dang chay thi phai
# khoi dong lai Javis moi thay (stop-javis.bat roi start-javis.vbs).
#
# KHONG dung ky tu co dau trong file .ps1: PowerShell tren Windows doc file khong BOM bang
# ANSI codepage, chu co dau se thanh rac ngay tren man hinh nguoi dung.
# ============================================================
param(
  [switch]$NoStart,      # cai xong khong tu bat server
  [switch]$NoAutostart,  # khong bat tu khoi dong cung Windows (mac dinh BAT tu 0.306.0)
  [switch]$SkipCli       # bo qua buoc cai 4 CLI (chi cai Python deps)
)

$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

function Line($t) { Write-Host $t }
function Step($n, $t) { Write-Host "" ; Write-Host "[$n] $t" -ForegroundColor Cyan }
function Ok($t) { Write-Host "    OK  $t" -ForegroundColor Green }
function Warn($t) { Write-Host "    [!] $t" -ForegroundColor Yellow }
function Err($t) { Write-Host "    [LOI] $t" -ForegroundColor Red }

# PATH cua phien hien tai KHONG tu cap nhat sau khi mot installer ghi vao registry. Doc lai
# ca Machine + User de buoc tong ket noi dung su that, va de `npm` vua cai bang winget dung
# duoc ngay trong cung mot luot chay.
function Refresh-Path {
  $m = [Environment]::GetEnvironmentVariable("Path", "Machine")
  $u = [Environment]::GetEnvironmentVariable("Path", "User")
  $env:PATH = (@($m, $u) | Where-Object { $_ }) -join ";"
}

function Have($cmd) { return [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }

Line ""
Line " =========================================="
Line "  AAROHI Companion - Windows setup"
Line " =========================================="

# ---------------------------------------------------------------- [1] Python
Step 1 "Kiem tra Python"
if (-not (Have "python")) {
  if (Have "winget") {
    Line "    Chua co Python, dang cai bang winget..."
    winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements | Out-Null
    Refresh-Path
  }
}
if (-not (Have "python")) {
  Err "Chua co Python. Tai Python 3.12 o python.org, tick 'Add python.exe to PATH', roi chay lai file nay."
  exit 1
}
$pyv = (python --version 2>&1)
Ok "$pyv"

# ---------------------------------------------------------------- [2] venv + deps
Step 2 "Cai thu vien Python (venv)"
if (-not (Test-Path ".venv")) {
  python -m venv .venv
  if ($LASTEXITCODE -ne 0) { Err "Khong tao duoc .venv"; exit 1 }
}
$vpy = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $vpy)) { Err "Thieu .venv\Scripts\python.exe - xoa thu muc .venv roi chay lai."; exit 1 }
& $vpy -m pip install --upgrade pip -q
& $vpy -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
  Err "pip install THAT BAI. Server se bao 'thieu claude-agent-sdk' neu bo qua buoc nay."
  Line "    Thu lai: .venv\Scripts\python.exe -m pip install -r requirements.txt"
  Line "    Hay gap loi UnicodeDecodeError thi may dang thieu Visual C++ Build Tools / mang chan pypi."
  exit 1
}
Ok "Da cai xong thu vien (gom claude-agent-sdk)"

# Desktop control (Mark-capability clean-room): optional but installed for companion OS
Step "2b" "Cai desktop control (pyautogui + pillow)"
& $vpy -m pip install pyautogui pillow -q
if ($LASTEXITCODE -eq 0) { Ok "Desktop control deps ready" }
else { Warn "pyautogui/pillow chua cai duoc - Aarohi van chay; screenshot/click se bao thieu goi" }

# ---------------------------------------------------------------- [3] Node + 4 CLI
if ($SkipCli) {
  Step 3 "Bo qua buoc cai CLI (-SkipCli)"
} else {
  Step 3 "Cai 4 bo nao CLI (chay bang goi thue bao, khong can mua API key)"
  if (-not (Have "npm")) {
    if (Have "winget") {
      Line "    Chua co Node.js, dang cai bang winget..."
      winget install -e --id OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements | Out-Null
      Refresh-Path
    }
  }
  if (Have "npm") {
    foreach ($it in @(
      @{ pkg = "@anthropic-ai/claude-code"; bin = "claude"; ten = "Claude Code" },
      @{ pkg = "@openai/codex"; bin = "codex"; ten = "Codex - goi ChatGPT" }
    )) {
      if (Have $it.bin) { Ok "$($it.ten): da co san"; continue }
      Line "    $($it.ten): dang cai (npm install -g $($it.pkg))..."
      cmd /c "npm install -g $($it.pkg)" | Out-Null
      Refresh-Path
      if (Have $it.bin) { Ok "$($it.ten)" } else { Warn "$($it.ten) cai chua duoc. Cai tay: npm install -g $($it.pkg)" }
    }
  } else {
    Warn "Chua co Node.js nen bo qua Claude Code + Codex. Cai Node LTS o nodejs.org roi chay lai file nay."
  }

  # agy va grok KHONG cai bang npm: moi nha mot script cai rieng. Best-effort tung cai -
  # mot cai hong khong duoc chan ba cai con lai.
  foreach ($it in @(
    @{ bin = "agy"; ten = "Antigravity CLI (Google)"; url = "https://antigravity.google/cli/install.ps1" },
    @{ bin = "grok"; ten = "Grok Build (xAI)"; url = "https://x.ai/cli/install.ps1" }
  )) {
    if (Have $it.bin) { Ok "$($it.ten): da co san"; continue }
    Line "    $($it.ten): dang cai tu $($it.url) ..."
    try {
      $sc = (Invoke-RestMethod -Uri $it.url -UseBasicParsing -TimeoutSec 60)
      Invoke-Expression $sc
      Refresh-Path
      if (Have $it.bin) { Ok "$($it.ten)" } else { Warn "$($it.ten): script chay xong nhung chua thay binary. Mo PowerShell moi roi thu: irm $($it.url) | iex" }
    } catch {
      Warn "$($it.ten) cai chua duoc ($($_.Exception.Message)). Cai tay: irm $($it.url) | iex"
    }
  }
}

# ---------------------------------------------------------------- [4] .env
Step 4 "Kiem tra .env"
if ((-not (Test-Path ".env")) -and (Test-Path "env.example")) {
  Copy-Item "env.example" ".env"
  Ok "Da tao .env tu env.example"
} else {
  Ok ".env da co"
}

# Companion voice defaults (Hinglish Swara at -8%) when settings exist
$settingsPath = Join-Path $Root "server\settings.json"
if (Test-Path $settingsPath) {
  try {
    & $vpy -c @"
import json
from pathlib import Path
p = Path(r'$settingsPath')
cfg = json.loads(p.read_text(encoding='utf-8'))
loc = cfg.setdefault('locale', {})
loc.setdefault('reply_lang', 'hi')
loc.setdefault('ui_lang', 'en')
v = cfg.setdefault('voice', {})
v.setdefault('edge_voice', 'hi-IN-SwaraNeural')
v['tts_rate'] = v.get('tts_rate') or '-8%'
cfg['_tts_rate_hint'] = '-8%'
# Enable desktop plugins when present
for slug in ('desktop-control', 'desktop-apps'):
    plugs = cfg.setdefault('plugins', {})
    if isinstance(plugs, dict) and slug in plugs:
        plugs[slug] = True if not isinstance(plugs[slug], dict) else {**plugs[slug], 'enabled': True}
p.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('ok')
"@
    Ok "Companion defaults: Hinglish + Swara -8%"
  } catch { Warn "Could not pin voice defaults in settings.json" }
}

# ---------------------------------------------------------------- [5] port 7777
Step 5 "Giai phong port 7777"
$conns = Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue
if ($conns) {
  foreach ($c in $conns) {
    try { Stop-Process -Id $c.OwningProcess -Force -ErrorAction Stop; Ok "Da tat tien trinh cu PID $($c.OwningProcess)" }
    catch { Warn "Khong tat duoc PID $($c.OwningProcess) - dong tay roi chay lai." }
  }
} else {
  Ok "Port 7777 dang trong"
}

# ---------------------------------------------------------------- tong ket
Refresh-Path
Line ""
Line " =========================================="
Line "  BO NAO SAN SANG (chon o trang Models)"
Line " =========================================="
foreach ($it in @(
  @{ bin = "claude"; ten = "Claude Code    " },
  @{ bin = "codex"; ten = "Codex (ChatGPT)" },
  @{ bin = "agy"; ten = "Antigravity CLI" },
  @{ bin = "grok"; ten = "Grok Build     " }
)) {
  if (Have $it.bin) {
    $p = (Get-Command $it.bin).Source
    Write-Host "  [x] $($it.ten)  $p" -ForegroundColor Green
  } else {
    Write-Host "  [ ] $($it.ten)  chua cai" -ForegroundColor Yellow
  }
}
Line ""
Line "  Dang nhap tung bo nao NGAY TRONG trang Models cua dashboard - khong can go lenh."
Line "  After installing more CLIs, restart AAROHI (stop-javis.bat then AAROHI-start.bat),"
Line "  because the running process keeps the PATH from when it started."
Line ""

# Desktop shortcut
Step "5c" "Desktop shortcut"
try {
  $desk = [Environment]::GetFolderPath("Desktop")
  $lnkPath = Join-Path $desk "AAROHI.lnk"
  $w = New-Object -ComObject WScript.Shell
  $lnk = $w.CreateShortcut($lnkPath)
  $lnk.TargetPath = Join-Path $Root "AAROHI-start.bat"
  $lnk.WorkingDirectory = $Root
  $lnk.Description = "AAROHI Companion"
  $ico = Join-Path $Root "dashboard\logo.png"
  if (Test-Path $ico) { $lnk.IconLocation = "$ico,0" }
  $lnk.Save()
  Ok "Desktop shortcut: AAROHI.lnk"
} catch { Warn "Could not create Desktop shortcut: $($_.Exception.Message)" }

# ---------------------------------------------------------------- [5b] tu khoi dong
# 0.306.0: default autostart on Windows. Off: -NoAutostart, javis-autostart.bat uninstall,
# or Settings in the dashboard.
if (-not $NoAutostart) {
  $as = Join-Path $Root "javis-autostart.ps1"
  if (Test-Path $as) {
    & powershell -NoProfile -ExecutionPolicy Bypass -File $as install | Out-Null
    if ($LASTEXITCODE -eq 0) { Ok "Windows autostart: ON (AAROHI opens after login)" }
    else { Warn "Autostart not set. Later: javis-autostart.bat install" }
  }
}

# ---------------------------------------------------------------- [6] bat server
if ($NoStart) {
  Line "  Setup done. Start with AAROHI-start.bat (background) or setup.bat (console)."
  exit 0
}
Step 6 "Start AAROHI"
$vbs = Join-Path $Root "start-javis.vbs"
if (Test-Path $vbs) {
  # /open: wait for server then open dashboard (0.306.0).
  Start-Process "wscript.exe" -ArgumentList "//nologo `"$vbs`" /open" -WorkingDirectory $Root
  Ok "Server running in background; dashboard will open. Log: server\javis.log"
} else {
  Start-Process $vpy -ArgumentList "main.py" -WorkingDirectory (Join-Path $Root "server")
  Ok "Server running"
}
Line ""
Line "  Open: http://127.0.0.1:7777"
Line ""
