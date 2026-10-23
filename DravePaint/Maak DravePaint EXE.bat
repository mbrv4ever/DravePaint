@echo off
setlocal enabledelayedexpansion
title DravePaint EXE bouwen

rem --- Een Python zoeken: keten 3.13 - 3.10, anders python ---
set "PY="
for %%V in (3.13 3.12 3.11 3.10) do (
    if not defined PY (
        py -%%V -c "import sys" >nul 2>&1 && set "PY=py -%%V"
    )
)
if not defined PY (
    python -c "import sys" >nul 2>&1 && set "PY=python"
)
if not defined PY (
    echo Geen Python gevonden. Installeer Python 3.10 t/m 3.13 van python.org.
    pause
    exit /b 1
)

echo Benodigde pakketten controleren / installeren...
!PY! -m pip install --upgrade PyQt6 Pillow pyinstaller

echo.
echo EXE bouwen ^(onefile^)...
!PY! -m PyInstaller --noconfirm --clean DravePaint.spec

echo.
echo Klaar. De EXE staat in de map dist\.
pause
endlocal
