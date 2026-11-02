# Optional AAROHI girlfriend voice stack:
#   TTS: Indic-Speak (Kavya)  ~6.6 GB gated HF model
#   STT: Shruti               ~29.5 MB
#
# Usage:
#   $env:HF_TOKEN = "hf_..."   # required for Indic-Speak download after accepting model terms
#   powershell -ExecutionPolicy Bypass -File scripts\install-aarohi-voice.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$py = if (Test-Path ".venv\Scripts\python.exe") { ".venv\Scripts\python.exe" } else { "python" }
Write-Host "Python: $py"
Write-Host "Installing STT (Shruti / cactus-needle)..."
& $py -m pip install -U "cactus-needle" "huggingface_hub"

Write-Host "Installing TTS runtime deps for Indic-Speak (torch + transformers + snac)..."
& $py -m pip install -U "transformers>=5" "snac" "soundfile" "numpy"
# CPU torch if nothing present; skip if user already has CUDA torch
& $py -c "import torch" 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Host "Installing CPU torch (replace with CUDA build yourself if you have a GPU)..."
  & $py -m pip install -U torch --index-url https://download.pytorch.org/whl/cpu
}

$env:NEEDLE_TELEMETRY = "0"
Write-Host "Prefetching Shruti weights..."
& $py -c "from huggingface_hub import hf_hub_download; print(hf_hub_download('udgamlabs/Shruti','shruti.cact'))"

if (-not ($env:HF_TOKEN -or $env:HUGGING_FACE_HUB_TOKEN)) {
  Write-Host ""
  Write-Host "HF_TOKEN not set. Accept Indic-Speak terms on Hugging Face, then:"
  Write-Host '  $env:HF_TOKEN="hf_..."'
  Write-Host "  python -c `"from huggingface_hub import snapshot_download; print(snapshot_download('bodhan-ai/indic-speak-preview-v2'))`""
  Write-Host "Until then Aarohi keeps Edge Swara as the free girlfriend voice."
} else {
  Write-Host "Prefetching Indic-Speak (this is large)..."
  & $py -c "from huggingface_hub import snapshot_download; import os; print(snapshot_download('bodhan-ai/indic-speak-preview-v2', token=os.environ.get('HF_TOKEN') or os.environ.get('HUGGING_FACE_HUB_TOKEN')))"
}

Write-Host ""
Write-Host "Done. Restart Aarohi, then Settings > Voice > Kavya when available."
Write-Host "Docs: docs/aarohi/VOICE_GIRLFRIEND.md"
