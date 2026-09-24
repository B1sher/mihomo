@echo off
chcp 65001 >nul
title Push Mihomo Rules

cd /d "%~dp0"

:: Get ESC symbol
for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"

:: Purple header
echo %ESC%[35m============================================%ESC%[0m
echo %ESC%[35m   Push Mihomo Rules to GitHub%ESC%[0m
echo %ESC%[35m============================================%ESC%[0m
echo.

:: [1/4] ADD - GOLD
echo %ESC%[33m[1/4]%ESC%[0m Adding changes...
git add .

:: [2/4] COMMIT - GOLD
echo %ESC%[33m[2/4]%ESC%[0m Committing...
git commit -m "update: rules %date% %time%"

:: [3/4] PULL - GOLD
echo %ESC%[33m[3/4]%ESC%[0m Pulling latest changes...
git pull --rebase
if errorlevel 1 (
    echo.
    echo %ESC%[31m[ERROR]%ESC%[0m Pull failed. Resolve conflicts manually.
    pause
    exit /b 1
)

:: [4/4] PUSH - GOLD
echo %ESC%[33m[4/4]%ESC%[0m Pushing to GitHub...
git push
if errorlevel 1 (
    echo.
    echo %ESC%[31m[ERROR]%ESC%[0m Push failed. Check your connection.
    pause
    exit /b 1
)

echo.
:: Green final
echo %ESC%[32m============================================%ESC%[0m
echo %ESC%[32m   Done!%ESC%[0m
echo %ESC%[32m============================================%ESC%[0m
echo.

timeout /t 2 >nul
exit