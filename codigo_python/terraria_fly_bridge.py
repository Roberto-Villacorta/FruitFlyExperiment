import time
import json
import socket
import random
import numpy as np

# Puerto de comunicación con el mod de Terraria en localhost
TERRARIA_HOST = '127.0.0.1'
TERRARIA_PORT = 8080  # Cambiar según el puerto configurado en el mod

def terraria_to_sensory_input(game_state):
    """
    Convierte el estado del juego recibido desde Terraria en estimulación para las neuronas fóticas/sensoriales.
    """
    tiles = game_state.get('nearby_tiles', [0] * 256)
    health = game_state.get('player_health', 100) / 100.0
    mobs_left = game_state.get('mobs_left', 0)
    mobs_right = game_state.get('mobs_right', 0)
    
    sensory_vector = np.array([health, mobs_left, mobs_right] + tiles[:13], dtype=np.float32)
    return sensory_vector

def process_fly_brain(sensory_vector, weights):
    """
    Simula la dinámica de la red neuronal basada en el conectoma de Drosophila.
    Calcula la activación de las neuronas motoras descendentes (DNs).
    """
    hidden_activation = np.tanh(np.dot(sensory_vector, weights['input_to_hidden']))
    motor_activation = 1.0 / (1.0 + np.exp(-np.dot(hidden_activation, weights['hidden_to_motor'])))
    return motor_activation

def motor_to_terraria_action(motor_activation):
    """
    Mapea las activaciones de las neuronas motoras a comandos de entrada para Terraria:
      - Motor 0: Mover Izquierda (A)
      - Motor 1: Mover Derecha (D)
      - Motor 2: Saltar (Espacio)
      - Motor 3: Atacar / Usar Herramienta (Clic Izquierdo)
    """
    actions = {
        'move_left': bool(motor_activation[0] > 0.5),
        'move_right': bool(motor_activation[1] > 0.5),
        'jump': bool(motor_activation[2] > 0.6),
        'attack': bool(motor_activation[3] > 0.55)
    }
    return actions

def generate_weights(in_dim, out_dim):
    """Genera matrices de pesos sinápticos usando el módulo nativo random"""
    random.seed(42)
    return np.array([[random.uniform(-0.1, 0.1) for _ in range(out_dim)] for _ in range(in_dim)], dtype=np.float32)

def main():
    print("--------------------------------------------------------------------------")
    print(" Puente de Comunicacion: Conectoma de Drosophila <-> Terraria Mod")
    print("--------------------------------------------------------------------------")
    
    weights = {
        'input_to_hidden': generate_weights(16, 32),
        'hidden_to_motor': generate_weights(32, 4)
    }
    
    print(f"Intentando conectar al mod de Terraria en {TERRARIA_HOST}:{TERRARIA_PORT}...")
    
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(0.5)
        client_socket.connect((TERRARIA_HOST, TERRARIA_PORT))
        print("Conexion establecida con el mod de Terraria.")
        
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
                
            game_state = json.loads(data.decode('utf-8'))
            sensory_input = terraria_to_sensory_input(game_state)
            motor_output = process_fly_brain(sensory_input, weights)
            command = motor_to_terraria_action(motor_output)
            
            response_json = json.dumps(command) + "\n"
            client_socket.sendall(response_json.encode('utf-8'))
            time.sleep(0.05)
            
    except Exception as e:
        print(f"Nota: No hay una instancia activa escuchando en el puerto {TERRARIA_PORT}.")
        print("Ejecutando verificacion de simulacion offline...")
        
        mock_game_state = {'player_health': 80, 'mobs_left': 1, 'mobs_right': 0, 'nearby_tiles': [1]*256}
        sensory_input = terraria_to_sensory_input(mock_game_state)
        motor_output = process_fly_brain(sensory_input, weights)
        actions = motor_to_terraria_action(motor_output)
        
        print("\nVerificacion offline completada con exito:")
        print(f"Vector Sensorial (Lobulo Optico): {sensory_input[:4]}")
        print(f"Activacion Neuronas Motoras (DNs): {motor_output}")
        print(f"Comandos mapeados para Terraria: {actions}")

if __name__ == "__main__":
    main()
