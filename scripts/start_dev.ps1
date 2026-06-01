$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$Frontend = Join-Path $Root "frontend"
$Python = Join-Path $Root "venv\Scripts\python.exe"
$BackendLog = Join-Path $Root "uvicorn.log"
$BackendErrLog = Join-Path $Root "uvicorn.err.log"

if (-not (Test-Path $Python)) {
    throw "Virtual environment not found. Run: python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt"
}

if (-not (Test-Path (Join-Path $Frontend "node_modules"))) {
    Push-Location $Frontend
    npm install
    Pop-Location
}

$BackendConnection = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue |
    Where-Object { $_.State -eq "Listen" -and $_.LocalAddress -in @("127.0.0.1", "0.0.0.0", "::") } |
    Select-Object -First 1

if (-not $BackendConnection) {
    Write-Host "Starting FastAPI on http://127.0.0.1:8000 ..."
    Start-Process `
        -FilePath $Python `
        -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload" `
        -WorkingDirectory $Root `
        -WindowStyle Hidden `
        -RedirectStandardOutput $BackendLog `
        -RedirectStandardError $BackendErrLog
}
else {
    Write-Host "FastAPI is already listening on http://127.0.0.1:8000"
}

$Ready = $false
for ($Attempt = 1; $Attempt -le 20; $Attempt++) {
    try {
        Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:8000/health" | Out-Null
        $Ready = $true
        break
    }
    catch {
        Start-Sleep -Milliseconds 500
    }
}

if (-not $Ready) {
    Write-Host "FastAPI did not become ready. Backend log:"
    if (Test-Path $BackendErrLog) {
        Get-Content $BackendErrLog -Tail 40
    }
    throw "Backend startup failed. See uvicorn.err.log for details."
}

Write-Host "Starting React on http://127.0.0.1:5173 ..."
Push-Location $Frontend
npm run dev
Pop-Location
