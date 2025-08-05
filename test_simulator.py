#!/usr/bin/env python3
"""
Archivo de pruebas para el Simulador de Red
Demuestra el funcionamiento de todos los módulos
"""

import sys
import os

# Añadir el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from network import Network
from config_manager import ConfigManager
from cli_parser import CLIParser

def test_data_structures():
    """Prueba las estructuras de datos"""
    print("=== Prueba de Estructuras de Datos ===")
    
    from data_structures import LinkedList, Queue, Stack
    
    # Prueba Lista Enlazada
    print("\n1. Prueba Lista Enlazada:")
    ll = LinkedList()
    ll.append("Router1")
    ll.append("Switch1")
    ll.append("PC1")
    print(f"   Lista: {ll.to_list()}")
    print(f"   Tamaño: {ll.get_size()}")
    print(f"   Contiene 'Switch1': {ll.contains('Switch1')}")
    
    # Prueba Cola
    print("\n2. Prueba Cola:")
    queue = Queue()
    queue.enqueue("Paquete1")
    queue.enqueue("Paquete2")
    queue.enqueue("Paquete3")
    print(f"   Cola: {queue.to_list()}")
    print(f"   Primer elemento: {queue.peek()}")
    print(f"   Desencolado: {queue.dequeue()}")
    print(f"   Cola después: {queue.to_list()}")
    
    # Prueba Pila
    print("\n3. Prueba Pila:")
    stack = Stack()
    stack.push("Historial1")
    stack.push("Historial2")
    stack.push("Historial3")
    print(f"   Pila: {stack.to_list()}")
    print(f"   Cima: {stack.peek()}")
    print(f"   Desapilado: {stack.pop()}")
    print(f"   Pila después: {stack.to_list()}")

def test_packet():
    """Prueba la clase Packet"""
    print("\n=== Prueba de Paquetes ===")
    
    from packet import Packet
    
    packet = Packet("192.168.1.1", "192.168.1.2", "Hola mundo", 5)
    print(f"Paquete creado: {packet}")
    print(f"TTL inicial: {packet.ttl}")
    
    packet.add_hop("Router1")
    packet.add_hop("Switch1")
    print(f"Camino: {packet.get_path_string()}")
    
    packet.decrement_ttl()
    print(f"TTL después de decremento: {packet.ttl}")
    print(f"¿Expirado? {packet.is_expired()}")

def test_device_and_interface():
    """Prueba las clases Device e Interface"""
    print("\n=== Prueba de Dispositivos e Interfaces ===")
    
    from device import Device, Interface
    
    # Crear dispositivo
    router = Device("Router1", "router")
    print(f"Dispositivo creado: {router}")
    
    # Añadir interfaces
    router.add_interface("g0/0", "192.168.1.1")
    router.add_interface("g0/1", "10.0.0.1")
    
    # Configurar interfaces
    g0_0 = router.get_interface("g0/0")
    g0_0.no_shutdown()
    g0_1 = router.get_interface("g0/1")
    g0_1.shutdown()
    
    print(f"Interfaces de {router.name}:")
    for name, interface in router.interfaces.items():
        print(f"  {interface}")

def test_network():
    """Prueba la clase Network"""
    print("\n=== Prueba de Red ===")
    
    network = Network()
    
    # Añadir dispositivos
    network.add_device("Router1", "router")
    network.add_device("Switch1", "switch")
    network.add_device("PC1", "host")
    network.add_device("PC2", "host")
    
    # Configurar interfaces
    router = network.get_device("Router1")
    router.add_interface("g0/0", "192.168.1.1")
    router.add_interface("g0/1", "10.0.0.1")
    
    switch = network.get_device("Switch1")
    switch.add_interface("g0/1", "192.168.1.2")
    switch.add_interface("g0/2", "192.168.1.3")
    
    pc1 = network.get_device("PC1")
    pc1.add_interface("eth0", "10.0.0.2")
    
    pc2 = network.get_device("PC2")
    pc2.add_interface("eth0", "192.168.1.4")
    
    # Activar interfaces
    for device in network.devices.values():
        for interface in device.get_interfaces():
            interface.no_shutdown()
    
    # Conectar dispositivos
    network.connect_interfaces("Router1", "g0/0", "Switch1", "g0/1")
    network.connect_interfaces("Router1", "g0/1", "PC1", "eth0")
    network.connect_interfaces("Switch1", "g0/2", "PC2", "eth0")
    
    print(f"Red creada con {len(network.devices)} dispositivos")
    print(f"Conexiones: {len(network.connections)}")
    
    # Enviar paquete
    success, message = network.send_packet("10.0.0.2", "192.168.1.4", "Prueba de comunicación")
    print(f"Envio de paquete: {message}")
    
    # Procesar paquetes
    result = network.process_packets()
    print(f"Procesamiento: {result}")
    
    # Mostrar estadísticas
    stats = network.get_network_statistics()
    print(f"Estadísticas: {stats}")

def test_cli_parser():
    """Prueba el parser CLI"""
    print("\n=== Prueba del Parser CLI ===")
    
    network = Network()
    config_manager = ConfigManager()
    parser = CLIParser(network, config_manager)
    
    # Configurar red básica
    network.add_device("Router1", "router")
    router = network.get_device("Router1")
    router.add_interface("g0/0", "192.168.1.1")
    router.get_interface("g0/0").no_shutdown()
    
    # Probar comandos
    commands = [
        "show devices",
        "enable",
        "configure terminal",
        "hostname Router1",
        "interface g0/1",
        "ip address 10.0.0.1",
        "no shutdown",
        "exit",
        "exit",
        "show interfaces"
    ]
    
    print("Ejecutando comandos CLI:")
    for cmd in commands:
        result = parser.parse_command(cmd)
        print(f"  {cmd} -> {result}")

def test_config_manager():
    """Prueba el gestor de configuración"""
    print("\n=== Prueba del Gestor de Configuración ===")
    
    network = Network()
    config_manager = ConfigManager()
    
    # Crear configuración de prueba
    test_config = {
        "devices": {
            "Router1": {
                "name": "Router1",
                "type": "router",
                "status": "online",
                "interfaces": {
                    "g0/0": {
                        "name": "g0/0",
                        "ip_address": "192.168.1.1",
                        "status": "up"
                    }
                }
            }
        },
        "connections": [],
        "current_device": "Router1"
    }
    
    # Cargar configuración
    success, message = config_manager.load_from_dict(network, test_config)
    print(f"Carga de configuración: {message}")
    
    # Guardar configuración
    success, message = config_manager.save_config(network, "test_config.json")
    print(f"Guardado de configuración: {message}")
    
    # Exportar CLI
    success, message = config_manager.export_cli_config(network, "test_running-config.txt")
    print(f"Exportación CLI: {message}")

def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("Iniciando pruebas del Simulador de Red...")
    print("=" * 50)
    
    try:
        test_data_structures()
        test_packet()
        test_device_and_interface()
        test_network()
        test_cli_parser()
        test_config_manager()
        
        print("\n" + "=" * 50)
        print("Todas las pruebas completadas exitosamente!")
        print("\nPara usar el simulador interactivo, ejecuta:")
        print("python main.py")
        
    except Exception as e:
        print(f"\nError en las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests() 