import os
import sys
import urllib.request
import h5py
import numpy as np
import imageio.v2 as imageio

# Directorio base para guardar los archivos de datos (en la raiz del proyecto)
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

def ensure_data_dir():
    """Crea la carpeta de datos si aun no existe en el proyecto."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Directorio creado en: {DATA_DIR}")

def download_file(url, output_path, timeout=5):
    """
    Intenta descargar un archivo remoto desde una URL dada.
    Si la conexion falla o vence el tiempo de espera, permite continuar con datos sinteticos.
    """
    print(f"Descargando datos desde: {url}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=timeout) as response, open(output_path, 'wb') as out_file:
            out_file.write(response.read())
        print("Descarga completada correctamente.")
        return True
    except Exception as e:
        print(f"El recurso remoto no esta disponible actualmente ({e}). Se generara un volumen de prueba local.")
        return False

def generate_fruitfly_synthetic_em_sample():
    """
    Genera un volumen 3D sintético que simula micrografías electrónicas (EM) del tejido cerebral
    de Drosophila melanogaster, junto con sus etiquetas de segmentación celular para pruebas locales.
    """
    sample_h5_path = os.path.join(DATA_DIR, "fruitfly_sample_volume.h5")
    sample_tif_path = os.path.join(DATA_DIR, "train-input.tif")
    label_h5_path = os.path.join(DATA_DIR, "train_label.h5")

    print("Generando volumen 3D sintético de micrografía electrónica...")
    
    depth, height, width = 64, 256, 256
    
    # Coordenadas espaciales del volumen
    z_coords = np.arange(depth)[:, None, None]
    y_coords = np.arange(height)[None, :, None]
    x_coords = np.arange(width)[None, None, :]
    
    # Centros de estructuras neuronales simuladas
    center1 = (height // 3, width // 3)
    center2 = (2 * height // 3, 2 * width // 3)
    center3 = (height // 2, width // 2)
    
    dist1 = np.sqrt((y_coords - center1[0])**2 + (x_coords - center1[1])**2)
    dist2 = np.sqrt((y_coords - center2[0])**2 + (x_coords - center2[1])**2)
    dist3 = np.sqrt((y_coords - center3[0])**2 + (x_coords - center3[1])**2)
    
    dist1_3d = np.tile(dist1, (depth, 1, 1))
    dist2_3d = np.tile(dist2, (depth, 1, 1))
    dist3_3d = np.tile(dist3, (depth, 1, 1))
    
    # Simulación de intensidad de grises y textura microscópica
    raw_em = 180.0 + 30.0 * np.sin(dist1_3d / 10.0) + 20.0 * np.cos(dist2_3d / 12.0)
    noise = np.sin(z_coords * 0.5 + y_coords * 0.1 + x_coords * 0.1) * 15.0
    raw_em = np.clip(raw_em + noise, 0, 255).astype(np.uint8)
    
    # Máscaras de segmentación con identificadores únicos para cada región celular
    segmentation = np.zeros((depth, height, width), dtype=np.uint32)
    segmentation[dist1_3d < 45] = 101
    segmentation[dist2_3d < 40] = 202
    segmentation[dist3_3d < 30] = 303
    
    # Guardar en formato HDF5
    with h5py.File(sample_h5_path, 'w') as f:
        f.create_dataset('raw', data=raw_em, compression='gzip')
        f.create_dataset('label', data=segmentation, compression='gzip')
    print(f"Volumen HDF5 guardado en: {sample_h5_path}")

    with h5py.File(label_h5_path, 'w') as f:
        f.create_dataset('main', data=segmentation, compression='gzip')
    print(f"Máscara de segmentación HDF5 guardada en: {label_h5_path}")

    # Guardar imagen en formato TIFF de 3 dimensiones
    imageio.volwrite(sample_tif_path, raw_em)
    print(f"Volumen en formato TIFF guardado en: {sample_tif_path}")

def main():
    ensure_data_dir()
    print("--- Descarga y preparación de volúmenes para la mosca de la fruta ---")
    
    # Enlace de muestra del dataset de Connectomics
    public_snemi_url = "https://connectomics.readthedocs.io/en/latest/_downloads/snemi3d_sample.h5"
    download_file(public_snemi_url, os.path.join(DATA_DIR, "snemi3d_sample.h5"))
    
    # Creación de volúmenes de respaldo en caso de trabajar offline
    generate_fruitfly_synthetic_em_sample()
    
    print("Todos los datos de entrenamiento e inferencia están listos en la carpeta 'data/'.")

if __name__ == "__main__":
    main()
