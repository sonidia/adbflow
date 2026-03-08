@echo off
echo Installing dependencies...

mkdir C:\android-tools
cd /d C:\android-tools

curl -L -o platform-tools.zip https://dl.google.com/android/repository/platform-tools-latest-windows.zip
tar -xf platform-tools.zip
del platform-tools.zip

curl -L -o scrcpy.zip https://github.com/Genymobile/scrcpy/releases/download/v3.3.4/scrcpy-win64-v3.3.4.zip
tar -xf scrcpy.zip
del scrcpy.zip

echo Checking PATH...

echo %PATH% | find /I "C:\android-tools\platform-tools" >nul
if errorlevel 1 (
    echo Adding platform-tools to PATH
    setx PATH "%PATH%;C:\android-tools\platform-tools"
) else (
    echo platform-tools already in PATH
)

echo %PATH% | find /I "C:\android-tools\scrcpy-win64-v3.3.4" >nul
if errorlevel 1 (
    echo Adding scrcpy to PATH
    setx PATH "%PATH%;C:\android-tools\scrcpy-win64-v3.3.4"
) else (
    echo scrcpy already in PATH
)

echo DONE. Restart CMD to use.
pause
