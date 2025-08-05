"""
Simulador de Red de Dispositivos (LAN) — CLI Estilo Router
Desarrollado para el curso de Algoritmos y Estructuras de Datos II
"""

import json
import os
from network import Network
from cli_parser import CLIParser
from config_manager import ConfigManager

def load_default_config():
    """Carga la configuración por defecto para pruebas"""
    return {
        "devices": [
            {
                "name": "Router1",
                "type": "router",
                "interfaces": [
                    {"name": "g0/0", "ip": "192.168.1.1", "status": "up"},
                    {"name": "g0/1", "ip": "10.0.0.1", "status": "up"}
                ]
            },
            {
                "name": "Switch1", 
                "type": "switch",
                "interfaces": [
                    {"name": "g0/1", "ip": "192.168.1.2", "status": "up"},
                    {"name": "g0/2", "ip": "192.168.1.3", "status": "up"}
                ]
            },
            {
                "name": "PC1",
                "type": "host", 
                "interfaces": [
                    {"name": "eth0", "ip": "10.0.0.2", "status": "up"}
                ]
            },
            {
                "name": "PC2",
                "type": "host",
                "interfaces": [
                    {"name": "eth0", "ip": "192.168.1.4", "status": "up"}
                ]
            }
        ],
        "connections": [
            ["Router1", "g0/0", "Switch1", "g0/1"],
            ["Router1", "g0/1", "PC1", "eth0"],
            ["Switch1", "g0/2", "PC2", "eth0"]
        ]
    }

def main():
    """Función principal del simulador"""
    print("=== Simulador de Red de Dispositivos (LAN) ===")
    print("CLI Estilo Router - Algoritmos II")
    print("Escriba 'help' para ver comandos disponibles")
    print("Escriba 'exit' para salir")
    print("-" * 50)
    
    # Inicializar la red
    network = Network()
    config_manager = ConfigManager()
    
    # Cargar configuración por defecto si no existe archivo de configuración
    config_file = "network_config.json"
    if os.path.exists(config_file):
        try:
            config_manager.load_config(network, config_file)
            print(f"Configuración cargada desde {config_file}")
        except Exception as e:
            print(f"Error al cargar configuración: {e}")
            print("Cargando configuración por defecto...")
            config_manager.load_from_dict(network, load_default_config())
    else:
        print("Cargando configuración por defecto...")
        config_manager.load_from_dict(network, load_default_config())
    
    # Inicializar parser CLI
    parser = CLIParser(network, config_manager)
    
    # Bucle principal de comandos
    try:
        while True:
            try:
                # Usar el prompt del parser CLI en lugar de acceder directamente
                prompt = parser.get_prompt()
                command = input(prompt).strip()
                if not command:
                    continue
                    
                if command.lower() in ['exit', 'quit']:
                    print("Guardando configuración antes de salir...")
                    config_manager.save_config(network, config_file)
                    print("¡Hasta luego!")
                    break
                    
                result = parser.parse_command(command)
                if result:
                    print(result)
                    
            except KeyboardInterrupt:
                print("\nGuardando configuración antes de salir...")
                config_manager.save_config(network, config_file)
                print("¡Hasta luego!")
                break
            except Exception as e:
                print(f"Error: {e}")
                
    except EOFError:
        print("\nGuardando configuración antes de salir...")
        config_manager.save_config(network, config_file)
        print("¡Hasta luego!")

if __name__ == "__main__":
    main() 