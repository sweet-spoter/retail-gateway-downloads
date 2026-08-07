@echo off
echo Cloudflare Tunnel - Service Manager
echo Store: elsupermarket_store_01
echo.
echo  [1] Start tunnel
echo  [2] Stop tunnel
echo  [3] Restart tunnel
echo  [4] Check status
echo  [5] View live tunnel logs
echo  [6] Uninstall tunnel service
echo  [Q] Quit
echo.
set /p CHOICE="Select option: "

if /i "%CHOICE%"=="1" (
    sc start cloudflared
    echo Tunnel started.
)
if /i "%CHOICE%"=="2" (
    sc stop cloudflared
    echo Tunnel stopped.
)
if /i "%CHOICE%"=="3" (
    sc stop cloudflared
    timeout /t 2 >nul
    sc start cloudflared
    echo Tunnel restarted.
)
if /i "%CHOICE%"=="4" (
    sc query cloudflared
    echo.
    curl -s https://elsupermarkets-store001.store-proxycfargotunnel.win/health
)
if /i "%CHOICE%"=="5" (
    cloudflared tunnel info elsupermarket_store_01
)
if /i "%CHOICE%"=="6" (
    sc stop cloudflared
    cloudflared service uninstall
    echo Tunnel service removed.
)
if /i "%CHOICE%"=="Q" exit /b 0

pause
