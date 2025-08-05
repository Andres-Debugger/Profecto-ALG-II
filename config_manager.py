"""
Gestor de Configuración para el Simulador de Red
Maneja la persistencia de configuraciones en formato JSON
"""

import json
import os
from device import Device, Interface

class ConfigManager:
    """Gestiona la carga y guardado de configuraciones de red"""
    
    def __init__(self):
        """Inicializa el gestor de configuración"""
        pass
    
    def save_config(self, network, filename="network_config.json"):
        """
        Guarda la configuración actual de la red en un archivo JSON
        
        Args:
            network: Instancia de Network a guardar
            filename (str): Nombre del archivo de configuración
        """
        try:
            config_data = network.to_dict()
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            return True, f"Configuración guardada exitosamente en {filename}"
        except Exception as e:
            return False, f"Error al guardar configuración: {e}"
    
    def load_config(self, network, filename="network_config.json"):
        """
        Carga una configuración desde un archivo JSON
        
        Args:
            network: Instancia de Network donde cargar la configuración
            filename (str): Nombre del archivo de configuración
        """
        try:
            if not os.path.exists(filename):
                return False, f"El archivo {filename} no existe"
            
            with open(filename, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            return self.load_from_dict(network, config_data)
        except Exception as e:
            return False, f"Error al cargar configuración: {e}"
    
    def load_from_dict(self, network, config_data):
        """
        Carga una configuración desde un diccionario
        
        Args:
            network: Instancia de Network donde cargar la configuración
            config_data (dict): Datos de configuración
        """
        try:
            # Limpiar la red actual
            network.devices.clear()
            network.connections.clear()
            network.current_device = None
            
            # Cargar dispositivos
            if "devices" in config_data:
                for device_name, device_data in config_data["devices"].items():
                    # Crear dispositivo
                    device = Device(device_name, device_data.get("type", "host"))
                    device.set_status(device_data.get("status", "online"))
                    
                    # Cargar interfaces
                    if "interfaces" in device_data:
                        for interface_name, interface_data in device_data["interfaces"].items():
                            interface = Interface(interface_name, interface_data.get("ip_address"))
                            
                            # Establecer estado de la interfaz
                            if interface_data.get("status") == "up":
                                interface.no_shutdown()
                            else:
                                interface.shutdown()
                            
                            device.interfaces[interface_name] = interface
                    
                    # Cargar estadísticas
                    device.packets_processed = device_data.get("packets_processed", 0)
                    device.packets_dropped = device_data.get("packets_dropped", 0)
                    
                    network.devices[device_name] = device
            
            # Cargar conexiones
            if "connections" in config_data:
                for connection in config_data["connections"]:
                    if len(connection) == 4:
                        device1_name, interface1_name, device2_name, interface2_name = connection
                        success, message = network.connect_interfaces(
                            device1_name, interface1_name, device2_name, interface2_name
                        )
                        if not success:
                            print(f"Advertencia: {message}")
            
            # Establecer dispositivo actual
            if "current_device" in config_data and config_data["current_device"]:
                network.set_current_device(config_data["current_device"])
            elif network.devices:
                # Si no hay dispositivo actual, usar el primero
                first_device = list(network.devices.values())[0]
                network.current_device = first_device
            
            # Cargar estadísticas globales
            if "global_statistics" in config_data:
                network.global_statistics.update(config_data["global_statistics"])
            
            return True, "Configuración cargada exitosamente"
        except Exception as e:
            return False, f"Error al cargar configuración desde diccionario: {e}"
    
    def export_cli_config(self, network, filename="running-config.txt"):
        """
        Exporta la configuración en formato CLI (estilo Cisco)
        
        Args:
            network: Instancia de Network
            filename (str): Nombre del archivo de salida
        """
        try:
            cli_lines = []
            
            # Configuración de dispositivos
            for device in network.devices.values():
                cli_lines.append(f"hostname {device.name}")
                
                for interface_name, interface in device.interfaces.items():
                    cli_lines.append(f"interface {interface_name}")
                    
                    if interface.ip_address:
                        cli_lines.append(f"  ip address {interface.ip_address}")
                    
                    if interface.is_up():
                        cli_lines.append("  no shutdown")
                    else:
                        cli_lines.append("  shutdown")
                    
                    cli_lines.append("  exit")
                
                cli_lines.append("")  # Línea en blanco entre dispositivos
            
            # Conexiones
            cli_lines.append("# Conexiones entre dispositivos")
            for connection in network.connections:
                device1, interface1, device2, interface2 = connection
                cli_lines.append(f"connect {device1} {interface1} {device2} {interface2}")
            
            # Guardar archivo
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(cli_lines))
            
            return True, f"Configuración CLI exportada a {filename}"
        except Exception as e:
            return False, f"Error al exportar configuración CLI: {e}"
    
    def import_cli_config(self, network, filename="running-config.txt"):
        """
        Importa configuración desde formato CLI
        
        Args:
            network: Instancia de Network
            filename (str): Nombre del archivo de configuración CLI
        """
        try:
            if not os.path.exists(filename):
                return False, f"El archivo {filename} no existe"
            
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            current_device = None
            current_interface = None
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split()
                if not parts:
                    continue
                
                command = parts[0].lower()
                
                if command == "hostname" and len(parts) > 1:
                    device_name = parts[1]
                    if device_name not in network.devices:
                        network.add_device(device_name)
                    current_device = network.get_device(device_name)
                
                elif command == "interface" and len(parts) > 1 and current_device:
                    interface_name = parts[1]
                    current_device.add_interface(interface_name)
                    current_interface = current_device.get_interface(interface_name)
                
                elif command == "ip" and len(parts) > 2 and current_interface:
                    if parts[1] == "address":
                        ip_address = parts[2]
                        current_interface.set_ip_address(ip_address)
                
                elif command == "no" and len(parts) > 1 and current_interface:
                    if parts[1] == "shutdown":
                        current_interface.no_shutdown()
                
                elif command == "shutdown" and current_interface:
                    current_interface.shutdown()
                
                elif command == "exit":
                    if current_interface:
                        current_interface = None
                    elif current_device:
                        current_device = None
                
                elif command == "connect" and len(parts) > 3:
                    device1, interface1, device2, interface2 = parts[1:5]
                    network.connect_interfaces(device1, interface1, device2, interface2)
            
            return True, "Configuración CLI importada exitosamente"
        except Exception as e:
            return False, f"Error al importar configuración CLI: {e}" 