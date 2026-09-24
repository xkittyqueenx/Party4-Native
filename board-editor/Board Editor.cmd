@echo off
cd /d "%~dp0"
if exist "%LOCALAPPDATA%\Programs\Python\Python313\pythonw.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python313\pythonw.exe" "%~dp0board_editor.py"
    exit /b %errorlevel%
)
if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\pythonw.exe" (
    "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\pythonw.exe" "%~dp0board_editor.py"
    exit /b %errorlevel%
)
where py >nul 2>&1
if not errorlevel 1 (
    py -3 "%~dp0board_editor.py"
    exit /b %errorlevel%
)
where python >nul 2>&1
if not errorlevel 1 (
    python "%~dp0board_editor.py"
    exit /b %errorlevel%
)
echo Python 3 with Tkinter is required to run the Board Editor.
pause
