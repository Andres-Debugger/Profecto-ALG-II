"""
Estructuras de Datos (TDA) para el Simulador de Red
Implementación de Lista Enlazada, Cola y Pila
"""

class Node:
    """Nodo para estructuras de datos enlazadas"""
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    """Lista Enlazada Simple"""
    def __init__(self):
        self.head = None
        self.size = 0
    
    def append(self, data):
        """Añade un elemento al final de la lista"""
        new_node = Node(data)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self.size += 1
    
    def remove(self, data):
        """Elimina un elemento de la lista"""
        if not self.head:
            return False
        
        if self.head.data == data:
            self.head = self.head.next
            self.size -= 1
            return True
        
        current = self.head
        while current.next:
            if current.next.data == data:
                current.next = current.next.next
                self.size -= 1
                return True
            current = current.next
        return False
    
    def contains(self, data):
        """Verifica si un elemento está en la lista"""
        current = self.head
        while current:
            if current.data == data:
                return True
            current = current.next
        return False
    
    def to_list(self):
        """Convierte la lista enlazada a una lista Python"""
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result
    
    def is_empty(self):
        """Verifica si la lista está vacía"""
        return self.head is None
    
    def get_size(self):
        """Retorna el tamaño de la lista"""
        return self.size

class Queue:
    """Cola (FIFO - First In, First Out)"""
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0
    
    def enqueue(self, data):
        """Añade un elemento al final de la cola"""
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1
    
    def dequeue(self):
        """Elimina y retorna el primer elemento de la cola"""
        if not self.head:
            return None
        
        data = self.head.data
        self.head = self.head.next
        self.size -= 1
        
        if not self.head:
            self.tail = None
        
        return data
    
    def peek(self):
        """Retorna el primer elemento sin eliminarlo"""
        if not self.head:
            return None
        return self.head.data
    
    def is_empty(self):
        """Verifica si la cola está vacía"""
        return self.head is None
    
    def get_size(self):
        """Retorna el tamaño de la cola"""
        return self.size
    
    def to_list(self):
        """Convierte la cola a una lista Python"""
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result

class Stack:
    """Pila (LIFO - Last In, First Out)"""
    def __init__(self):
        self.head = None
        self.size = 0
    
    def push(self, data):
        """Añade un elemento a la cima de la pila"""
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        self.size += 1
    
    def pop(self):
        """Elimina y retorna el elemento de la cima de la pila"""
        if not self.head:
            return None
        
        data = self.head.data
        self.head = self.head.next
        self.size -= 1
        return data
    
    def peek(self):
        """Retorna el elemento de la cima sin eliminarlo"""
        if not self.head:
            return None
        return self.head.data
    
    def is_empty(self):
        """Verifica si la pila está vacía"""
        return self.head is None
    
    def get_size(self):
        """Retorna el tamaño de la pila"""
        return self.size
    
    def to_list(self):
        """Convierte la pila a una lista Python (orden inverso)"""
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result 