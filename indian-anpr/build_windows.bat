@echo off
setlocal

echo ========================================================
echo Building Offline Indian ANPR System Desktop Executable
echo ========================================================

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

pyinstaller --noconfirm --onedir --windowed ^
    --name "Indian_ANPR_Offline" ^
    --add-data "config.yaml;." ^
    --add-data "models;models" ^
    --hidden-import "ultralytics" ^
    --hidden-import "paddleocr" ^
    --hidden-import "PySide6" ^
    --hidden-import "sqlite3" ^
    app.py

echo.
echo ========================================================
echo Build complete. Executable in dist\Indian_ANPR_Offline\
echo Ensure models are placed in dist\Indian_ANPR_Offline\models\
echo ========================================================
pause
