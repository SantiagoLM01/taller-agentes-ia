# setup.ps1 — Instalación de un solo paso para el taller (Windows / PowerShell)
#
#   Ejecuta ESTO antes del taller:
#       .\setup.ps1
#
# Crea el entorno virtual, instala TODAS las dependencias con versiones fijadas,
# prepara el .env y verifica que todo quede listo.
#
# Si PowerShell bloquea la ejecución, abre PowerShell y corre una vez:
#       Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

Write-Host "`n=== Instalacion del taller de Agentes de IA (Windows) ===`n" -ForegroundColor Cyan

# 1. Verificar Python 3.10-3.12 (versiones probadas)
Write-Host "[1/5] Verificando Python..." -ForegroundColor Yellow
try {
    $ver = (& python --version) 2>&1
} catch {
    Write-Host "  X No se encontro 'python'. Instala Python 3.11 o 3.12 desde https://www.python.org/downloads/ y marca 'Add Python to PATH'." -ForegroundColor Red
    exit 1
}
if ($ver -match "(\d+)\.(\d+)") {
    $major = [int]$Matches[1]; $minor = [int]$Matches[2]
    if ($major -ne 3 -or $minor -lt 10) {
        Write-Host "  X Se encontro $ver. El taller requiere Python 3.10 o superior (recomendado: 3.11 o 3.12)." -ForegroundColor Red
        Write-Host "    Instala Python 3.12 desde https://www.python.org/downloads/release/python-3120/ y marca 'Add Python to PATH'." -ForegroundColor Red
        exit 1
    }
    if ($minor -ge 13) {
        Write-Host "  ! $ver detectado. Las dependencias se probaron en 3.11/3.12; con 3.13+ alguna libreria (p.ej. faiss-cpu) podria no tener wheel." -ForegroundColor Yellow
        Write-Host "    Si la instalacion falla, instala Python 3.12 y vuelve a correr .\setup.ps1" -ForegroundColor Yellow
    }
}
Write-Host "  OK $ver"

# 2. Crear el entorno virtual (si no existe)
Write-Host "[2/5] Creando entorno virtual (.venv)..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "  OK .venv ya existe (se reutiliza)."
} else {
    python -m venv .venv
    Write-Host "  OK .venv creado."
}

$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

# 3. Instalar dependencias
Write-Host "[3/5] Instalando dependencias (esto puede tardar unos minutos)..." -ForegroundColor Yellow
& $py -m pip install --upgrade pip --quiet
& $py -m pip install -r requirements.txt
Write-Host "  OK dependencias instaladas."

# 4. Preparar el .env
Write-Host "[4/5] Configurando .env..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  OK .env ya existe."
} else {
    Copy-Item ".env.example" ".env"
    Write-Host "  OK .env creado a partir de .env.example." -ForegroundColor Green
    Write-Host "  >> IMPORTANTE: abre .env y pega tus credenciales de Azure OpenAI." -ForegroundColor Magenta
}

# 5. Verificacion final
Write-Host "[5/5] Verificando el entorno..." -ForegroundColor Yellow
& $py setup_check.py

Write-Host "`n=== Listo. Si ves algun ADVERTENCIA sobre .env, edita el archivo .env y vuelve a correr:  .\.venv\Scripts\python.exe setup_check.py ===`n" -ForegroundColor Cyan
