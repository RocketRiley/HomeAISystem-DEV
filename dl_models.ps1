# dl_models.ps1 — simple fetcher for local-only assets
# Usage:  .\dl_models.ps1

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path ".\LLM-BASE" | Out-Null
New-Item -ItemType Directory -Force -Path ".\vrm" | Out-Null
New-Item -ItemType Directory -Force -Path ".\voice" | Out-Null
New-Item -ItemType Directory -Force -Path ".\wakewords" | Out-Null

# Fetch a small open-source LLM model
$ggufUrl = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
$ggufOut = ".\LLM-BASE\mistral-7b-instruct-v0.2.Q4_K_M.gguf"

if (-not (Test-Path $ggufOut)) {
  Write-Host "Downloading LLM model..." -ForegroundColor Cyan
  Invoke-WebRequest -Uri $ggufUrl -OutFile $ggufOut
}

# Example: copy your VRM manually into .\vrm (not downloaded here)
Write-Host "Place your .vrm model(s) into .\vrm" -ForegroundColor Yellow
Write-Host "Place voice models / wakewords into .\voice and .\wakewords" -ForegroundColor Yellow
Write-Host "Done." -ForegroundColor Green
