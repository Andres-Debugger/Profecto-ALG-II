"""
Clases Device e Interface para representar dispositivos de red
"""

from data_structures import Queue, Stack, LinkedList
from packet import Packet
import time

class Interface:
    """Representa una interfaz de red de un dispositivo"""
    
    def __init__(self, name, ip_address=None):
        """
        Inicializa una interfaz
        
        Args:
            name (str): Nombre de la interfaz (ej: g0/0, eth0)
            ip_address (str): Dirección IP de la interfaz
        """
        self.name = name
        self.ip_address = ip_address
        self.status = "down"  # down/up
        self.neighbors = LinkedList()  # Lista enlazada de vecinos
        self.input_queue = Queue()  # Cola de paquetes entrantes
        self.output_queue = Queue()  # Cola de paquetes salientes
    
    def set_ip_address(self, ip_address):
        """Establece la dirección IP de la interfaz"""
        self.ip_address = ip_address
    
    def shutdown(self):
        """Desactiva la interfaz"""
        self.status = "down"
    
    def no_shutdown(self):
        """Activa la interfaz"""
        self.status = "up"
    
    def is_up(self):
        """Verifica si la interfaz está activa"""
        return self.status == "up"
    
    def add_neighbor(self, neighbor_interface):
        """Añade un vecino a la interfaz"""
        if not self.neighbors.contains(neighbor_interface):
            self.neighbors.append(neighbor_interface)
    
    def remove_neighbor(self, neighbor_interface):
        """Elimina un vecino de la interfaz"""
        self.neighbors.remove(neighbor_interface)
    
    def get_neighbors(self):
        """Retorna la lista de vecinos"""
        return self.neighbors.to_list()
    
    def enqueue_input(self, packet):
        """Añade un paquete a la cola de entrada"""
        self.input_queue.enqueue(packet)
    
    def enqueue_output(self, packet):
        """Añade un paquete a la cola de salida"""
        self.output_queue.enqueue(packet)
    
    def dequeue_input(self):
        """Extrae un paquete de la cola de entrada"""
        return self.input_queue.dequeue()
    
    def dequeue_output(self):
        """Extrae un paquete de la cola de salida"""
        return self.output_queue.dequeue()
    
    def has_input_packets(self):
        """Verifica si hay paquetes en la cola de entrada"""
        return not self.input_queue.is_empty()
    
    def has_output_packets(self):
        """Verifica si hay paquetes en la cola de salida"""
        return not self.output_queue.is_empty()
    
    def get_input_queue_size(self):
        """Retorna el tamaño de la cola de entrada"""
        return self.input_queue.get_size()
    
    def get_output_queue_size(self):
        """Retorna el tamaño de la cola de salida"""
        return self.output_queue.get_size()
    
    def to_dict(self):
        """Convierte la interfaz a diccionario para serialización"""
        return {
            "name": self.name,
            "ip_address": self.ip_address,
            "status": self.status,
            "neighbors": self.neighbors.to_list()
        }
    
    def __str__(self):
        """Representación string de la interfaz"""
        status_icon = "✓" if self.is_up() else "✗"
        return f"{self.name} ({self.ip_address}) [{status_icon}]"

class Device:
    """Representa un dispositivo de red (router, switch, host, firewall)"""
    
    def __init__(self, name, device_type="host"):
        """
        Inicializa un dispositivo
        
        Args:
            name (str): Nombre del dispositivo
            device_type (str): Tipo de dispositivo (router, switch, host, firewall)
        """
        self.name = name
        self.type = device_type
        self.status = "online"  # online/offline
        self.interfaces = {}  # Diccionario de interfaces por nombre
        self.history = Stack()  # Pila para historial de paquetes recibidos
        self.packets_processed = 0
        self.packets_dropped = 0
    
    def add_interface(self, interface_name, ip_address=None):
        """Añade una interfaz al dispositivo"""
        if interface_name not in self.interfaces:
            self.interfaces[interface_name] = Interface(interface_name, ip_address)
            return True
        return False
    
    def remove_interface(self, interface_name):
        """Elimina una interfaz del dispositivo"""
        if interface_name in self.interfaces:
            del self.interfaces[interface_name]
            return True
        return False
    
    def get_interface(self, interface_name):
        """Obtiene una interfaz por nombre"""
        return self.interfaces.get(interface_name)
    
    def get_interfaces(self):
        """Retorna todas las interfaces del dispositivo"""
        return list(self.interfaces.values())
    
    def get_interface_by_ip(self, ip_address):
        """Busca una interfaz por dirección IP"""
        for interface in self.interfaces.values():
            if interface.ip_address == ip_address:
                return interface
        return None
    
    def set_status(self, status):
        """Establece el estado del dispositivo"""
        if status in ["online", "offline"]:
            self.status = status
    
    def is_online(self):
        """Verifica si el dispositivo está en línea"""
        return self.status == "online"
    
    def add_to_history(self, packet):
        """Añade un paquete al historial"""
        packet_info = {
            "timestamp": time.time(),
            "source_ip": packet.source_ip,
            "destination_ip": packet.destination_ip,
            "message": packet.message,
            "ttl_at_arrival": packet.ttl,
            "path": packet.get_path_string(),
            "expired": packet.is_expired()
        }
        self.history.push(packet_info)
        self.packets_processed += 1
    
    def get_history(self):
        """Retorna el historial de paquetes"""
        return self.history.to_list()
    
    def clear_history(self):
        """Limpia el historial de paquetes"""
        self.history = Stack()
        self.packets_processed = 0
        self.packets_dropped = 0
    
    def get_statistics(self):
        """Retorna estadísticas del dispositivo"""
        return {
            "name": self.name,
            "type": self.type,
            "status": self.status,
            "interfaces_count": len(self.interfaces),
            "packets_processed": self.packets_processed,
            "packets_dropped": self.packets_dropped,
            "history_size": self.history.get_size()
        }
    
    def to_dict(self):
        """Convierte el dispositivo a diccionario para serialización"""
        return {
            "name": self.name,
            "type": self.type,
            "status": self.status,
            "interfaces": {name: interface.to_dict() 
                          for name, interface in self.interfaces.items()},
            "packets_processed": self.packets_processed,
            "packets_dropped": self.packets_dropped
        }
    
    def __str__(self):
        """Representación string del dispositivo"""
        status_icon = "✓" if self.is_online() else "✗"
        return f"{self.name} ({self.type}) [{status_icon}]"
    
    def __repr__(self):
        return self.__str__() 