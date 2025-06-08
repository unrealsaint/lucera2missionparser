@echo off
REM Build the XML Reward Editor as a standalone EXE with icon

REM Install PyInstaller if not already installed
pip install pyinstaller

REM Remove previous build/dist folders
rmdir /s /q build
rmdir /s /q dist

echo Building with icon...
python -m PyInstaller --noconfirm --onefile --windowed --icon=img\Ologo.ico xml_editor.py

echo.
echo Build complete! Your exe is in the dist folder.
start dist
pause 