@echo off
setlocal DisableDelayedExpansion
chcp 65001 >nul
powershell.exe -NoProfile -ExecutionPolicy RemoteSigned -File "%~dp0scripts\install.ps1" %*
set "JARVIS_RESULT=%ERRORLEVEL%"
if not "%JARVIS_RESULT%"=="0" echo A instalacao nao terminou. Consulte COMECE-AQUI.html e a mensagem acima.
pause
exit /b %JARVIS_RESULT%
