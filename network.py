"""
Clase Network para gestionar la topología de red y el procesamiento de paquetes
"""

from device import Device, Interface
from packet import Packet
import time

class Network:
    """Gestiona la topología de red y el procesamiento de paquetes"""
    
    def __init__(self):
        """Inicializa la red"""
        self.devices = {}  # Diccionario de dispositivos por nombre
        self.connections = []  # Lista de conexiones entre interfaces
        self.current_device = None  # Dispositivo actualmente seleccionado
        self.global_statistics = {
            "total_packets_sent": 0,
            "total_packets_delivered": 0,
            "total_packets_dropped": 0,
            "total_hops": 0
        }
    
    def add_device(self, name, device_type="host"):
        """Añade un dispositivo a la red"""
        if name not in self.devices:
            self.devices[name] = Device(name, device_type)
            if not self.current_device:
                self.current_device = self.devices[name]
            return True
        return False
    
    def remove_device(self, name):
        """Elimina un dispositivo de la red"""
        if name in self.devices:
            # Eliminar todas las conexiones del dispositivo
            self.connections = [conn for conn in self.connections 
                              if conn[0] != name and conn[2] != name]
            
            # Si era el dispositivo actual, cambiar a otro
            if self.current_device and self.current_device.name == name:
                remaining_devices = [d for d in self.devices.values() if d.name != name]
                self.current_device = remaining_devices[0] if remaining_devices else None
            
            del self.devices[name]
            return True
        return False
    
    def get_device(self, name):
        """Obtiene un dispositivo por nombre"""
        return self.devices.get(name)
    
    def get_devices(self):
        """Retorna todos los dispositivos"""
        return list(self.devices.values())
    
    def set_current_device(self, device_name):
        """Establece el dispositivo actual"""
        if device_name in self.devices:
            self.current_device = self.devices[device_name]
            return True
        return False
    
    def connect_interfaces(self, device1_name, interface1_name, device2_name, interface2_name):
        """Conecta dos interfaces de dispositivos diferentes"""
        device1 = self.get_device(device1_name)
        device2 = self.get_device(device2_name)
        
        if not device1 or not device2:
            return False, "Uno o ambos dispositivos no existen"
        
        interface1 = device1.get_interface(interface1_name)
        interface2 = device2.get_interface(interface2_name)
        
        if not interface1 or not interface2:
            return False, "Una o ambas interfaces no existen"
        
        # Crear la conexión bidireccional
        connection = (device1_name, interface1_name, device2_name, interface2_name)
        reverse_connection = (device2_name, interface2_name, device1_name, interface1_name)
        
        # Verificar que no exista ya la conexión
        if connection in self.connections or reverse_connection in self.connections:
            return False, "La conexión ya existe"
        
        # Añadir vecinos a las interfaces
        interface1.add_neighbor((device2_name, interface2_name))
        interface2.add_neighbor((device1_name, interface1_name))
        
        # Añadir a la lista de conexiones
        self.connections.append(connection)
        
        return True, "Conexión establecida exitosamente"
    
    def disconnect_interfaces(self, device1_name, interface1_name, device2_name, interface2_name):
        """Desconecta dos interfaces"""
        device1 = self.get_device(device1_name)
        device2 = self.get_device(device2_name)
        
        if not device1 or not device2:
            return False, "Uno o ambos dispositivos no existen"
        
        interface1 = device1.get_interface(interface1_name)
        interface2 = device2.get_interface(interface2_name)
        
        if not interface1 or not interface2:
            return False, "Una o ambas interfaces no existen"
        
        # Buscar y eliminar la conexión
        connection = (device1_name, interface1_name, device2_name, interface2_name)
        reverse_connection = (device2_name, interface2_name, device1_name, interface1_name)
        
        if connection in self.connections:
            self.connections.remove(connection)
        elif reverse_connection in self.connections:
            self.connections.remove(reverse_connection)
        else:
            return False, "La conexión no existe"
        
        # Eliminar vecinos de las interfaces
        interface1.remove_neighbor((device2_name, interface2_name))
        interface2.remove_neighbor((device1_name, interface1_name))
        
        return True, "Conexión eliminada exitosamente"
    
    def send_packet(self, source_ip, destination_ip, message, ttl=10):
        """Envía un paquete desde una IP origen a una IP destino"""
        # Crear el paquete
        packet = Packet(source_ip, destination_ip, message, ttl)
        packet.timestamp = time.time()
        
        # Encontrar la interfaz origen
        source_interface = None
        source_device = None
        
        for device in self.devices.values():
            for interface in device.get_interfaces():
                if interface.ip_address == source_ip:
                    source_interface = interface
                    source_device = device
                    break
            if source_interface:
                break
        
        if not source_interface:
            return False, f"No se encontró interfaz con IP {source_ip}"
        
        # Añadir el dispositivo origen al camino
        packet.add_hop(source_device.name)
        
        # Encolar en la interfaz origen
        source_interface.enqueue_output(packet)
        self.global_statistics["total_packets_sent"] += 1
        
        return True, "Paquete encolado para envío"
    
    def process_packets(self):
        """Procesa todos los paquetes en las colas de la red"""
        processed_count = 0
        delivered_count = 0
        dropped_count = 0
        
        # Procesar paquetes de salida de todas las interfaces
        for device in self.devices.values():
            if not device.is_online():
                continue
                
            for interface in device.get_interfaces():
                if not interface.is_up():
                    continue
                
                # Procesar cola de salida
                while interface.has_output_packets():
                    packet = interface.dequeue_output()
                    processed_count += 1
                    
                    # Verificar si el paquete ha expirado
                    if packet.is_expired():
                        dropped_count += 1
                        device.packets_dropped += 1
                        self.global_statistics["total_packets_dropped"] += 1
                        continue
                    
                    # Decrementar TTL
                    packet.decrement_ttl()
                    
                    # Buscar interfaz destino
                    destination_interface = None
                    destination_device = None
                    
                    for d in self.devices.values():
                        for i in d.get_interfaces():
                            if i.ip_address == packet.destination_ip:
                                destination_interface = i
                                destination_device = d
                                break
                        if destination_interface:
                            break
                    
                    # Si encontramos el destino
                    if destination_interface and destination_device.is_online():
                        packet.add_hop(destination_device.name)
                        destination_interface.enqueue_input(packet)
                        delivered_count += 1
                        self.global_statistics["total_packets_delivered"] += 1
                        destination_device.add_to_history(packet)
                    else:
                        # Reenviar a vecinos
                        forwarded = False
                        for neighbor_device_name, neighbor_interface_name in interface.get_neighbors():
                            neighbor_device = self.get_device(neighbor_device_name)
                            if neighbor_device and neighbor_device.is_online():
                                neighbor_interface = neighbor_device.get_interface(neighbor_interface_name)
                                if neighbor_interface and neighbor_interface.is_up():
                                    packet.add_hop(neighbor_device.name)
                                    neighbor_interface.enqueue_input(packet)
                                    forwarded = True
                                    break
                        
                        if not forwarded:
                            dropped_count += 1
                            device.packets_dropped += 1
                            self.global_statistics["total_packets_dropped"] += 1
        
        # Procesar paquetes de entrada (mover a cola de salida si es necesario)
        for device in self.devices.values():
            if not device.is_online():
                continue
                
            for interface in device.get_interfaces():
                if not interface.is_up():
                    continue
                
                while interface.has_input_packets():
                    packet = interface.dequeue_input()
                    
                    # Si es el destino final
                    if interface.ip_address == packet.destination_ip:
                        device.add_to_history(packet)
                    else:
                        # Reenviar a otra interfaz del mismo dispositivo
                        for other_interface in device.get_interfaces():
                            if other_interface != interface and other_interface.is_up():
                                for neighbor_device_name, neighbor_interface_name in other_interface.get_neighbors():
                                    neighbor_device = self.get_device(neighbor_device_name)
                                    if neighbor_device and neighbor_device.is_online():
                                        neighbor_interface = neighbor_device.get_interface(neighbor_interface_name)
                                        if neighbor_interface and neighbor_interface.is_up():
                                            other_interface.enqueue_output(packet)
                                            break
        
        return {
            "processed": processed_count,
            "delivered": delivered_count,
            "dropped": dropped_count
        }
    
    def get_network_statistics(self):
        """Retorna estadísticas globales de la red"""
        total_devices = len(self.devices)
        online_devices = sum(1 for d in self.devices.values() if d.is_online())
        total_connections = len(self.connections)
        
        avg_hops = 0
        if self.global_statistics["total_packets_delivered"] > 0:
            avg_hops = self.global_statistics["total_hops"] / self.global_statistics["total_packets_delivered"]
        
        return {
            "total_devices": total_devices,
            "online_devices": online_devices,
            "total_connections": total_connections,
            "total_packets_sent": self.global_statistics["total_packets_sent"],
            "total_packets_delivered": self.global_statistics["total_packets_delivered"],
            "total_packets_dropped": self.global_statistics["total_packets_dropped"],
            "average_hops_per_packet": round(avg_hops, 2)
        }
    
    def to_dict(self):
        """Convierte la red a diccionario para serialización"""
        return {
            "devices": {name: device.to_dict() for name, device in self.devices.items()},
            "connections": self.connections,
            "current_device": self.current_device.name if self.current_device else None,
            "global_statistics": self.global_statistics
        }
    
    def __str__(self):
        """Representación string de la red"""
        return f"Network with {len(self.devices)} devices and {len(self.connections)} connections" 