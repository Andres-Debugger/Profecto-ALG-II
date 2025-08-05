"""
Clase Packet para simular paquetes de red
Encapsula toda la información necesaria para el envío de datos
"""

import uuid
from data_structures import LinkedList

class Packet:
    """Representa un paquete de red con toda su información"""
    
    def __init__(self, source_ip, destination_ip, message, ttl=10):
        """
        Inicializa un nuevo paquete
        
        Args:
            source_ip (str): Dirección IP de origen
            destination_ip (str): Dirección IP de destino
            message (str): Contenido del mensaje
            ttl (int): Time To Live - número máximo de saltos
        """
        self.id = str(uuid.uuid4())[:8]  # ID único corto
        self.source_ip = source_ip
        self.destination_ip = destination_ip
        self.message = message
        self.ttl = ttl
        self.path = LinkedList()  # Lista enlazada para el camino recorrido
        self.timestamp = None  # Se establecerá al enviar
    
    def add_hop(self, device_name):
        """Añade un salto al camino del paquete"""
        self.path.append(device_name)
    
    def decrement_ttl(self):
        """Decrementa el TTL del paquete"""
        if self.ttl > 0:
            self.ttl -= 1
        return self.ttl
    
    def is_expired(self):
        """Verifica si el paquete ha expirado (TTL = 0)"""
        return self.ttl <= 0
    
    def get_path_string(self):
        """Retorna el camino como string para mostrar"""
        path_list = self.path.to_list()
        if not path_list:
            return "Sin camino registrado"
        return " → ".join(path_list)
    
    def to_dict(self):
        """Convierte el paquete a diccionario para serialización"""
        return {
            "id": self.id,
            "source_ip": self.source_ip,
            "destination_ip": self.destination_ip,
            "message": self.message,
            "ttl": self.ttl,
            "path": self.path.to_list(),
            "timestamp": self.timestamp
        }
    
    def __str__(self):
        """Representación string del paquete"""
        return (f"Packet {self.id}: {self.source_ip} → {self.destination_ip} "
                f"(TTL: {self.ttl}, Path: {self.get_path_string()})")
    
    def __repr__(self):
        return self.__str__() 