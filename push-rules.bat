@echo off
chcp 65001 >nul
title Push Mihomo Rules

echo ============================================
echo    Push Mihomo Rules to GitHub
echo ============================================
echo.

cd /d "%~dp0"

REM === TOKEN SETTINGS ===
REM Replace YOUR_TOKEN with your GitHub token
set "GITHUB_TOKEN=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"

if not "%GITHUB_TOKEN%"=="YOUR_TOKEN" (
    echo Setting token...
    git remote set-url origin https://%GITHUB_TOKEN%@github.com/B1sher/mihomo.git
    echo Token set.
    echo.
)

echo [1/3] Adding changes...
git add .

echo [2/3] Committing...
git commit -m "update: rules %date% %time%"

echo [3/3] Pushing to GitHub...
git push

echo.
echo ============================================
echo    Done! Press any key...
echo ============================================
pause >nul
