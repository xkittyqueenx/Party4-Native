@echo off
cd /d "%~dp0"
if not exist "board-mods.txt" (
    echo Export a board from Board Editor first.
    pause
    exit /b 1
)
set "PARTYBOARD_MOD_LIST=%~dp0board-mods.txt"
start "" "%~dp0Mario Party 4 Deluxe.exe"
