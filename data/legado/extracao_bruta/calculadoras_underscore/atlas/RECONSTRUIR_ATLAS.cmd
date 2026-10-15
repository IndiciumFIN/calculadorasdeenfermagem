@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0RECONSTRUIR_ATLAS.ps1"
pause
