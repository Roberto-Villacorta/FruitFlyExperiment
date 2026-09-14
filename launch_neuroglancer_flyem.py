import sys
import os
import time
import argparse
import neuroglancer

def launch_flyem_neuroglancer(port=9999, mode='flyem'):
    """
    Inicia un servidor local de Neuroglancer para explorar datos connectómicos de Drosophila melanogaster.
    Modos de ejecución disponibles:
      - 'flyem': Janelia FlyEM Hemibrain (Dataset público en Google Cloud Storage)
      - 'fafb': FAFB v14 (Full Adult Fly Brain EM)
      - 'local': Cargar volumen local de micrografía electrónica y máscara de segmentación
    """
    ip = '127.0.0.1'
    neuroglancer.set_server_bind_address(bind_address=ip, bind_port=port)
    
    viewer = neuroglancer.Viewer()
    
    print("--------------------------------------------------------------------------")
    print(" Servidor Neuroglancer para Connectómica de Drosophila melanogaster")
    print("--------------------------------------------------------------------------")
    print(f" Modo seleccionado: {mode.upper()}")
    
    with viewer.txn() as s:
        if mode == 'flyem':
            print("Cargando capa del dataset publico Janelia FlyEM Hemibrain...")
            s.layers['flyem_em'] = neuroglancer.ImageLayer(
                source='precomputed://gs://neuroglancer-janelia-flyem-hemibrain/emdata/clahe_yz/jpeg/'
            )
            s.layers['flyem_segmentation'] = neuroglancer.SegmentationLayer(
                source='precomputed://gs://neuroglancer-janelia-flyem-hemibrain/v1.0/segmentation',
                selected_alpha=0.4
            )
            
        elif mode == 'fafb':
            print("Cargando capa del dataset publico FAFB v14 (Full Adult Fly Brain)...")
            s.layers['fafb_em'] = neuroglancer.ImageLayer(
                source='precomputed://gs://neuroglancer-fafb-data/fafb_v14/fafb_v14_clahe'
            )
            s.layers['fafb_mesh'] = neuroglancer.SingleMeshLayer(
                source='vtk://https://storage.googleapis.com/neuroglancer-fafb-data/elmr-data/FAFB.surf.vtk.gz'
            )
            
        elif mode == 'local':
            import numpy as np
            import h5py
            
            data_dir = os.path.join(os.path.dirname(__file__), "data")
            raw_h5 = os.path.join(data_dir, "fruitfly_sample_volume.h5")
            pred_h5 = os.path.join(data_dir, "fruitfly_scanner_prediction.h5")
            
            if not os.path.exists(raw_h5):
                print("No se encontró el volumen local. Generando datos de prueba...")
                from download_public_data import generate_fruitfly_synthetic_em_sample, ensure_data_dir
                ensure_data_dir()
                generate_fruitfly_synthetic_em_sample()
                
            print(f"Cargando archivo de volumen local: {raw_h5}")
            with h5py.File(raw_h5, 'r') as f:
                im_data = np.array(f['raw'])
                
            if os.path.exists(pred_h5):
                print(f"Cargando predicción de la red neuronal: {pred_h5}")
                with h5py.File(pred_h5, 'r') as f:
                    seg_data = np.array(f['segmentation'])
            else:
                with h5py.File(raw_h5, 'r') as f:
                    seg_data = np.array(f['label'])
                    
            res = neuroglancer.CoordinateSpace(
                names=['z', 'y', 'x'],
                units=['nm', 'nm', 'nm'],
                scales=[30, 8, 8]
            )
            
            s.layers['raw_em'] = neuroglancer.ImageLayer(
                source=neuroglancer.LocalVolume(data=im_data, dimensions=res, volume_type='image')
            )
            s.layers['cell_segmentation'] = neuroglancer.SegmentationLayer(
                source=neuroglancer.LocalVolume(data=seg_data, dimensions=res, volume_type='segmentation'),
                selected_alpha=0.4
            )
            
    print("\n--------------------------------------------------------------------------")
    print(f" Servidor Neuroglancer activo en la siguiente dirección:")
    print(f" {viewer}")
    print("--------------------------------------------------------------------------")
    print(" Abre el enlace en Google Chrome para interactuar con la reconstruccion 3D.")
    print(" Presiona Ctrl+C en esta consola para finalizar el servidor.")
    print("--------------------------------------------------------------------------\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nServidor Neuroglancer detenido.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lanzador de Neuroglancer para Drosophila")
    parser.add_argument("--port", type=int, default=9999, help="Puerto de escucha para el servidor HTTP (por defecto: 9999)")
    parser.add_argument("--mode", type=str, choices=['flyem', 'fafb', 'local'], default='flyem',
                        help="Modo de visualizacion: flyem (Janelia Hemibrain), fafb (FAFB v14), local (inferencia local)")
    args = parser.parse_args()
    
    launch_flyem_neuroglancer(port=args.port, mode=args.mode)
