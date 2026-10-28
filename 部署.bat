@echo off
chcp 65001 >nul
rem 雙擊 = 把網站上傳到 Cloudflare Pages(niyan-laser-pages.pages.dev)
rem 只上傳網站需要的檔案(不含 素材來源/、字型、PDF)
cd /d "%~dp0"

set "OUT=%TEMP%\laser-deploy"
if exist "%OUT%" rmdir /s /q "%OUT%"
mkdir "%OUT%"

copy /y index.html "%OUT%" >nul
copy /y default-*.js "%OUT%" >nul
copy /y favicon.png "%OUT%" >nul
copy /y manifest.webmanifest "%OUT%" >nul
copy /y 賀卡色紙.png "%OUT%" >nul

echo 上傳中...
cd /d "%OUT%"
call npx wrangler pages deploy . --project-name=niyan-laser-pages --branch=main --commit-dirty=true

echo.
echo 完成後到 https://niyan-laser-pages.pages.dev 按 Ctrl+F5 重新整理
pause
