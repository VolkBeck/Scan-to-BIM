@echo off
TITLE Scan-to-BIM Setup & Installation
CLS

ECHO ========================================================
ECHO  Scan-to-BIM - Automatische Einrichtung (Windows)
ECHO ========================================================
ECHO.

REM ---------------------------------------------------------
REM 1. PYTHON 3.11 CHECK
REM ---------------------------------------------------------
ECHO [1/4] Pruefe Python 3.11 Installation...
py -3.11 --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 GOTO INSTALL_PYTHON

ECHO [OK] Python 3.11 gefunden.
GOTO CHECK_CC

:INSTALL_PYTHON
ECHO [FEHLER] Python 3.11 fehlt.
ECHO Installiere via Winget...
winget install -e --id Python.Python.3.11
ECHO.
ECHO [WICHTIG] Bitte starten Sie dieses Skript nach der Installation NEU!
PAUSE
EXIT /B

REM ---------------------------------------------------------
REM 2. CLOUDCOMPARE CHECK
REM ---------------------------------------------------------
:CHECK_CC
ECHO.
ECHO [2/4] Pruefe CloudCompare Installation...

IF EXIST "C:\Program Files\CloudCompare\CloudCompare.exe" GOTO CC_FOUND

ECHO [INFO] CloudCompare konnte im Standardpfad nicht gefunden werden.
ECHO Moechten Sie CloudCompare jetzt installieren? (J/N)
SET /P INST_CC="> "
IF /I "%INST_CC%"=="J" (
    winget install -e --id CloudCompare.CloudCompare
)
GOTO VENV_STEP

:CC_FOUND
ECHO [OK] CloudCompare ist bereits installiert.
GOTO VENV_STEP

REM ---------------------------------------------------------
REM 3. VENV ERSTELLEN
REM ---------------------------------------------------------
:VENV_STEP
ECHO.
ECHO [3/4] Richte virtuelle Umgebung (scan2bim_env) ein...
IF EXIST "scan2bim_env" GOTO VENV_EXISTS

ECHO    - Erstelle Python Environment...
py -3.11 -m venv scan2bim_env

IF NOT EXIST "scan2bim_env\Scripts\python.exe" (
    ECHO.
    ECHO [FEHLER] Venv konnte nicht erstellt werden.
    PAUSE
    EXIT /B
)
GOTO INSTALL_REQS

:VENV_EXISTS
ECHO [OK] Python Environment existiert bereits.
GOTO INSTALL_REQS

REM ---------------------------------------------------------
REM 4. INSTALLATION
REM ---------------------------------------------------------
:INSTALL_REQS
ECHO.
ECHO [4/4] Installiere Bibliotheken...
ECHO    * Aktiviere Environment...
call scan2bim_env\Scripts\activate.bat

ECHO    * Update pip...
python -m pip install --upgrade pip

ECHO    * Installiere Projekt im Editable Mode...
pip install -e .

ECHO.
ECHO ========================================================
ECHO  INSTALLATION ABGESCHLOSSEN!
ECHO ========================================================
ECHO.

REM ---------------------------------------------------------
REM 5. INFO FUER SPAETEREN START
REM ---------------------------------------------------------
ECHO  WICHTIG: So startest du das Programm spaeter manuell:
ECHO.
ECHO  Option A (Schnell):
ECHO    scan2bim_env\Scripts\python.exe main.py
ECHO.
ECHO  Option B (Klassisch):
ECHO    1. scan2bim_env\Scripts\activate.bat
ECHO    2. python main.py
ECHO.
ECHO --------------------------------------------------------

REM ---------------------------------------------------------
REM 6. JETZT STARTEN?
REM ---------------------------------------------------------
ECHO Moechtest du das Programm JETZT direkt starten? (J/N)
SET /P START_PROG="> "

IF /I "%START_PROG%"=="J" (
    ECHO.
    ECHO Starte main.py ...
    ECHO --------------------------------------------------------
    python main.py
    REM Pause, damit man Fehler sieht, falls es abstuerzt
    PAUSE
) ELSE (
    ECHO.
    ECHO Alles klar. Viel Erfolg beim naechsten Mal!
    PAUSE
)