@echo off
echo ========================================
echo    PC Control Bot - Autostart Setup
echo ========================================
echo.

REM Prüfe Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python ist nicht installiert!
    echo Lade es herunter von: https://python.org
    pause
    exit /b
)

echo [*] Python gefunden!

REM Installiere Abhängigkeiten
echo [*] Installiere Abhängigkeiten...
pip install -r requirements.txt

REM Erstelle Autostart-Verknüpfung
set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set SCRIPT_DIR=%~dp0

echo [*] Erstelle Autostart...
(
echo @echo off
echo cd /d "%SCRIPT_DIR%"
echo python main.py
echo pause
) > "%STARTUP_DIR%\pc_bot.bat"

echo.
echo ========================================
echo    ✅ Setup abgeschlossen!
echo.
echo    Der Bot startet automatisch mit Windows.
echo    Starte ihn jetzt: python main.py
echo ========================================
pause
