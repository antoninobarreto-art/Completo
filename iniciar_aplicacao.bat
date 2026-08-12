@echo off
title Servidor DOJOCHO - Porta 8000

cd /d "%~dp0"

echo ===================================================
echo Servidor DOJOCHO - Porta 8000
echo ===================================================
echo.

if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Ativando ambiente virtual (.venv)...
    call .venv\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    echo [INFO] Ativando ambiente virtual (venv)...
    call venv\Scripts\activate.bat
)

echo [INFO] Iniciando Uvicorn em http://localhost:8000...
echo.

python -m uvicorn app.main:app --reload --port 8000

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] Falha ao iniciar a aplicacao.
    pause
)
