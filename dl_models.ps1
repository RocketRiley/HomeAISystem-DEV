# dl_models.ps1 — simple fetcher for local-only assets
# Usage:  .\dl_models.ps1

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path ".\LLM-BASE" | Out-Null
New-Item -ItemType Directory -Force -Path ".\vrm" | Out-Null
New-Item -ItemType Directory -Force -Path ".\voice" | Out-Null
New-Item -ItemType Directory -Force -Path ".\wakewords" | Out-Null

# === EDIT THESE URLS ===
# Example GGUF (placeholder; replace with your actual link)
$ggufUrl = "https://YOUR-DOWNLOAD-URL/capybarahermes-2.5-mistral-7b.Q6_K.gguf"
$ggufOut = ".\LLM-BASE\capybarahermes-2.5-mistral-7b.Q6_K.gguf"

if (-not (Test-Path $ggufOut)) {
  Write-Host "Downloading LLM model..." -ForegroundColor Cyan
  Invoke-WebRequest -Uri $ggufUrl -OutFile $ggufOut
}

# Example: copy your VRM manually into .\vrm (not downloaded here)
Write-Host "Place your .vrm model(s) into .\vrm" -ForegroundColor Yellow
Write-Host "Place voice models / wakewords into .\voice and .\wakewords" -ForegroundColor Yellow
Write-Host "Done." -ForegroundColor Green
