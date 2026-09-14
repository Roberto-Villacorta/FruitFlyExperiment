# Entorno de Connectómica y Escáner Neuronal para Drosophila melanogaster

Este repositorio contiene la estructura de trabajo para procesar, segmentar y visualizar datos de micrografía electrónica (EM) del cerebro de la mosca de la fruta (*Drosophila melanogaster*). Utiliza redes neuronales convolucionales 3D en PyTorch con aceleración por GPU CUDA (NVIDIA A1000) e integración directa con el visualizador WebGL **Neuroglancer**.

---

## Estructura del Proyecto

- `setup_env.ps1`: Script de instalación automatizada en PowerShell (crea `.venv` e instala PyTorch CUDA y dependencias).
- `setup_env.bat`: Script equivalente para la consola de comandos de Windows (`cmd.exe`).
- `requirements.txt`: Especificación de librerías Python (`torch`, `neuroglancer`, `cloud-volume`, `h5py`, `imageio`, `scipy`).
- `download_public_data.py`: Script para obtener o sintetizar volúmenes de prueba 3D en la carpeta `data/`.
- `fruitfly_neural_net.py`: Inferencia de red neuronal 3D (`ResUNet3D`) optimizada para estimar afinidades de membrana y segmentación celular.
- `launch_neuroglancer_flyem.py`: Servidor web local para la exploración de los datasets **Janelia FlyEM Hemibrain** y **FAFB v14**.
- `local_dataset_viewer.py`: Flujo de trabajo integrado que corre la inferencia y despliega el visualizador localmente.

---

## Guía de Instalación y Uso

### 1. Creación del Entorno Virtual e Instalación de Dependencias

Ejecuta el script de preparación desde PowerShell:

```powershell
.\setup_env.ps1
```

*(Si utilizas la consola CMD de Windows, puedes ejecutar `setup_env.bat`)*

Este comando configurará la carpeta `.venv` e instalará PyTorch con soporte para tarjetas gráficas dedicadas NVIDIA.

### 2. Activación del Entorno Virtual

En cada nueva terminal de trabajo, activa el entorno virtual mediante:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Preparación de Datos de Entrada

Para descargar o generar los volúmenes de entrenamiento e inferencia:

```powershell
python download_public_data.py
```

Esto generará los volúmenes en formato HDF5 y TIFF dentro del directorio `data/`.

### 4. Ejecución del Escáner Neuronal 3D

Para procesar el volumen 3D utilizando la red neuronal convolucional:

```powershell
python fruitfly_neural_net.py
```

El resultado de la inferencia se guardará en `data/fruitfly_scanner_prediction.h5`.

### 5. Visualización Interactiva con Neuroglancer

- **Para visualizar el dataset público Janelia FlyEM Hemibrain**:
  ```powershell
  python launch_neuroglancer_flyem.py --mode flyem
  ```

- **Para visualizar el reconstruido FAFB v14 (Full Adult Fly Brain)**:
  ```powershell
  python launch_neuroglancer_flyem.py --mode fafb
  ```

- **Para explorar el volumen local procesado por la red neuronal**:
  ```powershell
  python local_dataset_viewer.py
  ```

Una vez ejecutado, abre la dirección URL mostrada (`http://127.0.0.1:9999/v/...`) en el navegador Google Chrome.

---

## Referencias y Citas Bibliográficas

Para la utilización de este software y la publicación de trabajos académicos basados en estos datos, deben citarse las siguientes fuentes originales:

1. **PyTorch Connectomics (Documentación y Framework)**:
   - Lin, Z., Dong, W., Wei, D., & Pfister, H. (2021). *PyTorch Connectomics: A Deep Learning Library for Cellular Morphology Analysis*. PyTorch Connectomics Documentation. 
   - URL: https://connectomics.readthedocs.io/en/latest/external/neuroglancer.html

2. **Google Neuroglancer**:
   - Google Connectomics Team. (2020). *Neuroglancer: WebGL-based viewer for volumetric data*. Google Research.
   - Repositorio oficial: https://github.com/google/neuroglancer

3. **Dataset Janelia FlyEM Hemibrain**:
   - Scheffer, L. K., Xu, C. S., Januszewski, M., Lu, Z., Takemura, S. Y., Hayworth, K. J., ... & Plaza, S. M. (2020). *A connectome and analysis of the adult Drosophila central brain*. **eLife**, 9, e57442. 
   - DOI: https://doi.org/10.7554/eLife.57442

4. **Dataset FAFB (Full Adult Fly Brain)**:
   - Zheng, Z., Lauritzen, J. S., Perlman, E., Robinson, C. G., Nichols, M., Milkie, D., ... & Bock, D. D. (2018). *A Complete Electron Microscopy Volume of the Female Adult Drosophila Brain*. **Cell**, 174(3), 730-743.
   - DOI: https://doi.org/10.1016/j.cell.2018.06.019
