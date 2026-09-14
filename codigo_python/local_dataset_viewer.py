import os
import sys
from fruitfly_neural_net import run_scanner_inference
from launch_neuroglancer_flyem import launch_flyem_neuroglancer

def main():
    print("--------------------------------------------------------------------------")
    print(" Escáner y visualizador local de connectómica (Drosophila melanogaster)")
    print("--------------------------------------------------------------------------")
    
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    pred_h5 = os.path.join(data_dir, "fruitfly_scanner_prediction.h5")
    
    # 1. Ejecución de la red neuronal si no se ha procesado previamente la inferencia
    if not os.path.exists(pred_h5):
        print("\nPaso 1: Ejecutando la inferencia de la red neuronal 3D...")
        run_scanner_inference()
    else:
        print(f"\nPaso 1: Utilizando la predicción existente en {pred_h5}")
        
    # 2. Apertura del servidor local de Neuroglancer
    print("\nPaso 2: Iniciando el servidor Neuroglancer con el volumen procesado...")
    launch_flyem_neuroglancer(port=9999, mode='local')

if __name__ == "__main__":
    main()
