@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Update-Game.ps1" -GameFolder "%~dp0"
if errorlevel 1 echo Update failed. Please close the game and check the error above.
pause
