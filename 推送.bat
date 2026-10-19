@echo off
chcp 65001 >nul
cd /d "%~dp0"
git add -A
git diff --cached --quiet && (echo 沒有需要推送的變更 & pause & exit /b)
git commit -m "更新 %date% %time%"
git push origin main
pause
