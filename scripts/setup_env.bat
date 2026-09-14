@echo off
rem Script de automatizacion para el simbolo del sistema en Windows

rem Cambiar al directorio raiz del proyecto (directorio padre de scripts/)
cd /d "%~dp0\.."

echo Creando el entorno virtual (.venv)...
python -m venv .venv

echo Activando el entorno virtual...
call .venv\Scripts\activate.bat

echo Actualizando pip, setuptools y wheel...
python -m pip install --upgrade pip setuptools wheel

echo Instalando PyTorch con soporte CUDA...
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo Instalando dependencias de Neuroglancer y Connectomics...
python -m pip install -r requirements.txt

echo Verificando la GPU y CUDA...
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA Available:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"

echo Entorno preparado correctamente.
pause
