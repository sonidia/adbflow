@echo off
echo ========================================
echo   Fatan Builder
echo ========================================
echo.

pyinstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller is not installed.
    echo Please install it with: pip install pyinstaller
    echo.
    pause
    exit /b 1
)

echo [INFO] PyInstaller found. Starting build process...
echo.

if exist build rmdir /s /q build 2>nul
if exist dist rmdir /s /q dist 2>nul

echo [INFO] Building executable...
echo.

pyinstaller --clean build.spec

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo         BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Executable created: dist\fatan.exe
    echo Size:
    for %%A in ("dist\fatan.exe") do echo   %%~zA bytes
    echo.
    echo Copying dependencies folder to dist...
    xcopy /E /I /Y data dist\data
    copy /Y installer.bat dist\installer.bat
    copy /Y how-to-run.txt dist\how-to-run.txt
    echo.
) else (
    echo.
    echo ========================================
    echo          BUILD FAILED!
    echo ========================================
    echo.
    echo Please check the error messages above.
    echo Common issues:
    echo   - Missing dependencies (run: pip install -r requirements.txt)
    echo   - PySide6 not installed
    echo   - Antivirus blocking the build process
    echo.
)

echo.
pause