@echo off
setlocal enabledelayedexpansion
title DravePaint

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
    echo.
    pause
    exit /b 1
)

rem --- Benodigde pakketten controleren / installeren ---
!PY! -c "import PyQt6, PIL" >nul 2>&1
if errorlevel 1 (
    echo Eenmalig de benodigde pakketten installeren ^(PyQt6, Pillow^)...
    echo Dit kan even duren.
    echo.
    !PY! -m pip install --upgrade PyQt6 Pillow
)

!PY! DravePaint.py
if errorlevel 1 (
    echo.
    echo === DravePaint is gestopt met een fout ===
    echo Zie hierboven, en/of het bestand dravepaint_fout.txt in deze map.
    echo.
    pause
)
endlocal
