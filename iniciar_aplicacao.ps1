# Script PowerShell para iniciar a aplicação DOJOCHO na porta 8000
Set-Location -Path $PSScriptRoot

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "🥋 Iniciando Aplicação DOJOCHO (Porta 8000)" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# Verifica ambiente virtual (.venv ou venv)
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    Write-Host "[INFO] Ativando ambiente virtual (.venv)..." -ForegroundColor Yellow
    .\.venv\Scripts\Activate.ps1
} elseif (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "[INFO] Ativando ambiente virtual (venv)..." -ForegroundColor Yellow
    .\venv\Scripts\Activate.ps1
}

$sys_ver = python -c "from app.version import VERSION; print(VERSION)" 2>$null
if ($sys_ver) {
    Write-Host "[INFO] Versão do Sistema: v$sys_ver" -ForegroundColor Green
}
Write-Host "[INFO] Iniciando servidor Uvicorn em http://localhost:8000..." -ForegroundColor Green
Write-Host ""

python -m uvicorn app.main:app --reload --port 8000
