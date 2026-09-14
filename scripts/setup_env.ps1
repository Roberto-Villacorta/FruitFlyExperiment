# Script de PowerShell para crear el entorno virtual de Python e instalar PyTorch con soporte CUDA y Neuroglancer

# Asegurar que la ruta de ejecucion sea la raiz del proyecto
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

Write-Host "Creando el entorno virtual (.venv)..." -ForegroundColor Green
python -m venv .venv

Write-Host "Activando el entorno virtual..." -ForegroundColor Green
& .\.venv\Scripts\Activate.ps1

Write-Host "Actualizando pip, setuptools y wheel..." -ForegroundColor Green
python -m pip install --upgrade pip setuptools wheel

Write-Host "Instalando PyTorch con soporte CUDA..." -ForegroundColor Green
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

Write-Host "Instalando librerias para Connectomics y Neuroglancer..." -ForegroundColor Green
python -m pip install -r requirements.txt

Write-Host "Verificando la instalacion de PyTorch y CUDA..." -ForegroundColor Green
python -c "import torch; print('PyTorch Version:', torch.__version__); print('CUDA Disponible:', torch.cuda.is_available()); print('Dispositivo GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"

Write-Host "Configuracion completada con exito." -ForegroundColor Green
