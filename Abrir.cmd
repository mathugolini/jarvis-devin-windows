@echo off
setlocal DisableDelayedExpansion
if not exist "%LOCALAPPDATA%\JarvisDevin\bin\jarvis-devin.cmd" (
  echo Execute Instalar.cmd primeiro.
  pause
  exit /b 1
)
call "%LOCALAPPDATA%\JarvisDevin\bin\jarvis-devin.cmd" %*
