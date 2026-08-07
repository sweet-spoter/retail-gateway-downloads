@echo off
setlocal enabledelayedexpansion

echo =====================================================
echo  Retail Gateway - Cloudflare Tunnel Setup
echo  Store  : elsupermarket_store_01
echo  Domain : elsupermarkets-store001.store-proxycfargotunnel.win
echo  Exposes: https://elsupermarkets-store001.store-proxycfargotunnel.win
echo           --> http://localhost:3005
echo =====================================================
echo.

:: -------------------------------------------------------
:: STEP 0 — Verify cloudflared is installed
:: -------------------------------------------------------
cloudflared --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: cloudflared is not installed or not in PATH.
    echo.
    echo Download and install from:
    echo   https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.msi
    echo.
    echo After installing, re-run this script.
    pause
    exit /b 1
)

:: -------------------------------------------------------
:: STEP 1 — Authenticate with Cloudflare
:: -------------------------------------------------------
echo [1/5] Logging in to Cloudflare...
echo       A browser window will open. Log in and select the domain:
echo       elsupermarkets-store001.store-proxycfargotunnel.win
echo.
cloudflared tunnel login
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Cloudflare login failed.
    pause
    exit /b 1
)
echo.

:: -------------------------------------------------------
:: STEP 2 — Create the named tunnel
:: -------------------------------------------------------
echo [2/5] Creating tunnel 'elsupermarket_store_01'...
cloudflared tunnel create elsupermarket_store_01
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo NOTE: If the error says the tunnel already exists, that is OK.
    echo       Continue by entering the existing tunnel UUID below.
    echo.
)

echo.
echo -------------------------------------------------------
echo  Copy the tunnel UUID shown above (format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
echo -------------------------------------------------------
set /p TUNNEL_UUID="Paste tunnel UUID here and press Enter: "

if "!TUNNEL_UUID!"=="" (
    echo ERROR: No UUID entered. Exiting.
    pause
    exit /b 1
)

:: -------------------------------------------------------
:: STEP 3 — Write config to ProgramData
:: -------------------------------------------------------
echo.
echo [3/5] Writing tunnel configuration...

set CONFIG_DIR=C:\ProgramData\cloudflared
mkdir "%CONFIG_DIR%" 2>nul

:: Copy credentials file
set CRED_SRC=%USERPROFILE%\.cloudflared\!TUNNEL_UUID!.json
if exist "!CRED_SRC!" (
    copy "!CRED_SRC!" "%CONFIG_DIR%\" >nul
    echo       Credentials file copied.
) else (
    echo WARNING: Credentials file not found at:
    echo          !CRED_SRC!
    echo          You may need to copy it manually.
)

:: Write config.yml
(
    echo # Cloudflare Tunnel Configuration
    echo # Store  : elsupermarket_store_01
    echo # Domain : elsupermarkets-store001.store-proxycfargotunnel.win
    echo.
    echo tunnel: !TUNNEL_UUID!
    echo credentials-file: %CONFIG_DIR%\!TUNNEL_UUID!.json
    echo.
    echo ingress:
    echo   # WebSocket live data stream
    echo   - hostname: elsupermarkets-store001.store-proxycfargotunnel.win
    echo     path: /ws/retail-gateway
    echo     service: http://localhost:8081
    echo     originRequest:
    echo       connectTimeout: 10s
    echo       keepAliveConnections: 10
    echo       keepAliveTimeout: 90s
    echo.
    echo   # Proxy REST API
    echo   - hostname: elsupermarkets-store001.store-proxycfargotunnel.win
    echo     service: http://localhost:3005
    echo     originRequest:
    echo       connectTimeout: 10s
    echo       keepAliveConnections: 10
    echo       keepAliveTimeout: 90s
    echo       httpHostHeader: localhost
    echo.
    echo   - service: http_status:404
) > "%CONFIG_DIR%\config.yml"

echo       Config written to: %CONFIG_DIR%\config.yml

:: -------------------------------------------------------
:: STEP 4 — Create DNS CNAME record
:: -------------------------------------------------------
echo.
echo [4/5] Creating DNS record (CNAME) on Cloudflare...
cloudflared tunnel route dns elsupermarket_store_01 elsupermarkets-store001.store-proxycfargotunnel.win
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: DNS route failed. You may need to add the CNAME manually
    echo          in the Cloudflare dashboard:
    echo            Name  : elsupermarkets-store001.store-proxycfargotunnel.win
    echo            Target: !TUNNEL_UUID!.cfargotunnel.com
    echo            Proxy : Proxied (orange cloud ON^)
)
echo.

:: -------------------------------------------------------
:: STEP 5 — Install as Windows Service and start
:: -------------------------------------------------------
echo [5/5] Installing cloudflared as Windows Service...
cloudflared service install --config "%CONFIG_DIR%\config.yml"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Service installation failed. Try running this script as Administrator.
    pause
    exit /b 1
)

sc start cloudflared >nul 2>&1
echo       Service started.

:: -------------------------------------------------------
:: Verify
:: -------------------------------------------------------
echo.
echo =====================================================
echo  Setup complete!
echo.
echo  Tunnel URL : https://elsupermarkets-store001.store-proxycfargotunnel.win
echo  Routes to  : http://localhost:3005
echo.
echo  Verify the tunnel is active:
echo    sc query cloudflared
echo    curl https://elsupermarkets-store001.store-proxycfargotunnel.win/health
echo =====================================================
echo.
pause
