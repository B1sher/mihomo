@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

REM ANSI color codes
set "PURPLE=[38;2;139;92;246m"
set "GREEN=[32m"
set "RED=[31m"
set "YELLOW=[33m"
set "CYAN=[36m"
set "RESET=[0m"

echo %PURPLE%    Push Mihomo Rules to GitHub%RESET%
echo %CYAN%--------------------------------------------------%RESET%

cd /d "%~dp0"

echo %YELLOW%[1/4]%RESET% Pulling latest changes...
git pull --rebase --autostash

if errorlevel 1 (
    echo.
    echo %RED%[ERROR]%RESET% Pull failed. Resolve conflicts manually.
    pause
    exit /b 1
)

echo %YELLOW%[2/4]%RESET% Adding changes...
git add .

echo %YELLOW%[3/4]%RESET% Committing...
git commit -m "update: %date% %time%"

echo %YELLOW%[4/4]%RESET% Pushing to GitHub...
git push

if errorlevel 1 (
    echo.
    echo %RED%[ERROR]%RESET% Push failed. Check your connection.
    pause
    exit /b 1
)

echo.
echo %CYAN%--------------------------------------------------%RESET%
echo %GREEN%    Done! Rules pushed to GitHub successfully.%RESET%
echo %CYAN%--------------------------------------------------%RESET%
echo %YELLOW%    Closing in 5 seconds...%RESET%
timeout /t 5 /nobreak >nul
exit /b 0
