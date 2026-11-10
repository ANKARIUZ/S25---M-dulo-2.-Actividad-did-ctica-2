$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { $python = "python" }
Write-Host "Reproduciendo experimentos y figuras..."
& $python run_all.py --force
Write-Host "Construyendo el artículo..."
& $python build_docx.py
Write-Host "Listo. Revise results/ y docs/."
