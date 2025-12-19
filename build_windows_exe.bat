@echo off
REM Build a standalone Windows executable for the HEIC to JPG converter.
REM Requires Python 3.10+ on PATH.

setlocal

echo Installing dependencies...
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt >nul
python -m pip install pyinstaller >nul

echo Building executable...
pyinstaller --noconfirm --onefile --windowed --name heic_to_jpg convert_heic_to_jpg.py

echo.
echo Build complete. Find the exe in the dist folder:
echo   %~dp0dist\heic_to_jpg.exe
echo.
pause

endlocal
