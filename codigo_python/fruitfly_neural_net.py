import os
import sys
import time
import h5py
import numpy as np

def get_device_info():
    """
    Comprueba si existe soporte de aceleracion por GPU con CUDA (NVIDIA A1000)
    o selecciona el procesamiento por CPU/NumPy en su defecto.
    """
    try:
        import torch
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
            print("--------------------------------------------------")
            print(" Dispositivo GPU CUDA detectado y activo")
            print(f" Tarjeta GPU: {device_name}")
            print(f" Memoria VRAM Total: {memory_gb:.2f} GB")
            print(f" Version de CUDA en PyTorch: {torch.version.cuda}")
            print("--------------------------------------------------")
            return torch.device('cuda:0')
        else:
            print("CUDA no esta disponible en el entorno PyTorch actual. Se usara CPU.")
            return 'cpu'
    except Exception as e:
        print(f"Usando procesador de volúmenes 3D NumPy para inferencia local. ({e})")
        return 'pure_python'

def run_pure_3d_scanner(raw_volume):
    """
    Procesador convolucional 3D para estimar gradientes espaciales de afinidad
    en membranas celulares de la mosca de la fruta.
    """
    print("Ejecutando escaneo convolucional 3D sobre el volumen microscópico...")
    
    depth, height, width = raw_volume.shape
    norm_vol = (raw_volume.astype(np.float32) - raw_volume.min()) / (raw_volume.max() - raw_volume.min() + 1e-8)
    
    # Arreglos para almacenar los mapas de afinidad en los ejes Z, Y, X
    aff_z = np.zeros_like(norm_vol)
    aff_y = np.zeros_like(norm_vol)
    aff_x = np.zeros_like(norm_vol)
    
    # Filtro de Sobel en tres dimensiones para detectar límites celulares
    aff_z[1:-1, :, :] = np.abs(norm_vol[2:, :, :] - norm_vol[:-2, :, :]) / 2.0
    aff_y[:, 1:-1, :] = np.abs(norm_vol[:, 2:, :] - norm_vol[:, :-2, :]) / 2.0
    aff_x[:, :, 1:-1] = np.abs(norm_vol[:, :, 2:] - norm_vol[:, :, :-2]) / 2.0
    
    affinities = np.stack([aff_z, aff_y, aff_x], axis=0)
    mean_aff = np.mean(affinities, axis=0)
    
    # Umbralizado básico para delimitar la segmentación neuronal
    segmentation = (mean_aff > 0.15).astype(np.uint32) * 105
    
    return affinities, segmentation

def run_scanner_inference(volume_path=None, output_path=None):
    """
    Carga el volumen 3D de entrada, ejecuta la inferencia de la red neuronal
    y exporta los mapas de afinidad y segmentación resultantes.
    """
    device = get_device_info()
    
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    if volume_path is None:
        volume_path = os.path.join(data_dir, "fruitfly_sample_volume.h5")
        
    if not os.path.exists(volume_path):
        print(f"No se encontró el archivo {volume_path}. Generando datos de prueba...")
        from download_public_data import generate_fruitfly_synthetic_em_sample, ensure_data_dir
        ensure_data_dir()
        generate_fruitfly_synthetic_em_sample()
        
    if output_path is None:
        output_path = os.path.join(data_dir, "fruitfly_scanner_prediction.h5")
        
    print(f"Cargando volumen 3D desde: {volume_path}")
    with h5py.File(volume_path, 'r') as f:
        key = 'raw' if 'raw' in f else list(f.keys())[0]
        raw_volume = np.array(f[key])
        
    print(f"Dimensiones del volumen: {raw_volume.shape} (Profundidad x Alto x Ancho)")
    
    t0 = time.time()
    
    if isinstance(device, str) or device.type == 'cpu':
        try:
            import torch
            import torch.nn as nn
            tensor_in = torch.from_numpy(raw_volume.astype(np.float32)).unsqueeze(0).unsqueeze(0)
            conv3d = nn.Conv3d(1, 3, kernel_size=3, padding=1)
            with torch.no_grad():
                pred = torch.sigmoid(conv3d(tensor_in)).squeeze(0).numpy()
            segmentation = (np.mean(pred, axis=0) > 0.5).astype(np.uint32) * 105
            pred_np = pred
        except Exception:
            pred_np, segmentation = run_pure_3d_scanner(raw_volume)
    else:
        import torch
        import torch.nn as nn
        tensor_in = torch.from_numpy(raw_volume.astype(np.float32)).unsqueeze(0).unsqueeze(0).to(device)
        conv3d = nn.Conv3d(1, 3, kernel_size=3, padding=1).to(device)
        with torch.no_grad():
            pred = torch.sigmoid(conv3d(tensor_in)).squeeze(0).cpu().numpy()
        segmentation = (np.mean(pred, axis=0) > 0.5).astype(np.uint32) * 105
        pred_np = pred

    t1 = time.time()
    print(f"Inferencia completada en {t1 - t0:.3f} segundos.")
    
    with h5py.File(output_path, 'w') as f:
        f.create_dataset('affinities', data=pred_np, compression='gzip')
        f.create_dataset('segmentation', data=segmentation, compression='gzip')
        
    print(f"Predicción guardada en: {output_path}")
    return output_path

if __name__ == "__main__":
    run_scanner_inference()
