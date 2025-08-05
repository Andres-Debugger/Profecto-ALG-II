# Simulador de Red de Dispositivos (LAN) — CLI Estilo Router

Este proyecto implementa un simulador de red de dispositivos con interfaz de línea de comandos inspirada en la consola IOS de Cisco. Permite crear, conectar y administrar distintos tipos de dispositivos virtuales (routers, switches, computadoras y firewalls) y simular el envío de paquetes de red.

## Características

### Módulo 1: Dispositivos y Red (4 ptos)
- ✅ Clase `Device` con nombre, tipo y conjunto de interfaces
- ✅ Clase `Interface` con direcciones IP y estados (shutdown/no shutdown)
- ✅ Conexiones físicas entre interfaces usando listas enlazadas
- ✅ Clase `Network` que orquesta dispositivos y gestiona topología
- ✅ Comandos: `enable`, `configure terminal`, `hostname`, `interface`, `ip address`, `shutdown`/`no shutdown`, `exit`, `connect`, `disconnect`, `set_device_status`, `list_devices`

### Módulo 2: Paquetes y Comunicación (4 ptos)
- ✅ Clase `Packet` con ID único, origen/destino, contenido, TTL y traza de ruta
- ✅ Simulación de envío de paquetes con colas de salida
- ✅ Procesamiento de paquetes con `tick`/`process`
- ✅ Decremento de TTL y descarte de paquetes expirados
- ✅ Historial de recepción en dispositivos destino

### Módulo 3: Estructuras de Datos (3 ptos)
- ✅ **Lista Enlazada**: Para almacenar vecinos de cada interfaz
- ✅ **Cola**: Para gestionar paquetes entrantes y salientes (FIFO)
- ✅ **Pila**: Para registrar historial de mensajes recibidos (LIFO)

### Módulo 4: Interfaz de Línea de Comandos (3 ptos)
- ✅ Parser que gestiona múltiples niveles de contexto:
  - Modo usuario (`Device>`)
  - Modo privilegiado (`Device#`)
  - Modo configuración global (`Device(config)#`)
  - Modo configuración de interfaz (`Device(config-if)#`)
- ✅ Patrón Comando implementado
- ✅ Validación de entrada y manejo de errores
- ✅ Comandos adicionales: `disable`, `end`, `show`, `save`, `load`

### Módulo 5: Estadísticas y Reportes (3 ptos)
- ✅ `show history <device>` - Historial de paquetes
- ✅ `show queue <device>` - Estado de colas
- ✅ `show interfaces` - Información de interfaces
- ✅ `show statistics` - Estadísticas globales de la red

### Módulo 6: Persistencia de Configuración (3 ptos)
- ✅ Guardado y carga de configuración en formato JSON
- ✅ Exportación/importación en formato CLI (estilo Cisco)
- ✅ Configuración por defecto para pruebas

## Instalación y Uso

### Requisitos
- Python 3.6 o superior

### Ejecución
```bash
python main.py
```

### Ejemplo de Sesión

```bash
=== Simulador de Red de Dispositivos (LAN) ===
CLI Estilo Router - Algoritmos II
Escriba 'help' para ver comandos disponibles
Escriba 'exit' para salir
--------------------------------------------------
Cargando configuración por defecto...
Router1> enable
Router1# configure terminal
Router1(config)# hostname Router1
Router1(config)# interface g0/0
Router1(config-if)# ip address 192.168.1.1
Router1(config-if)# no shutdown
Router1(config-if)# exit
Router1(config)# exit
Router1# connect g0/0 Switch1 g0/1
Router1# list_devices
Devices in network:
  - Router1 (online)
  - Switch1 (online)
  - PC1 (online)
  - PC2 (online)
```

### Comandos Principales

#### Modo Usuario
- `enable` - Entra al modo privilegiado
- `show devices` - Lista dispositivos
- `show interfaces` - Muestra interfaces del dispositivo actual
- `show history [device]` - Muestra historial de paquetes
- `show queue [device]` - Muestra colas de paquetes
- `show statistics` - Muestra estadísticas de la red
- `send <src_ip> <dst_ip> <msg> [ttl]` - Envía un paquete
- `tick` - Procesa paquetes en la red
- `help` - Muestra ayuda
- `exit` - Sale del simulador

#### Modo Privilegiado
- `configure terminal` - Entra al modo configuración
- `connect <if1> <dev2> <if2>` - Conecta interfaces
- `disconnect <if1> <dev2> <if2>` - Desconecta interfaces
- `disable` - Regresa al modo usuario
- `end` - Regresa al modo privilegiado desde cualquier modo

#### Modo Configuración
- `hostname <name>` - Cambia nombre del dispositivo
- `interface <name>` - Entra al modo configuración de interfaz
- `exit` - Regresa al modo privilegiado

#### Modo Configuración de Interfaz
- `ip address <ip>` - Establece dirección IP
- `shutdown` - Desactiva interfaz
- `no shutdown` - Activa interfaz
- `exit` - Regresa al modo configuración

## Estructura del Proyecto

```
proyect-alg2/
├── main.py                 # Archivo principal
├── data_structures.py      # TDA: Lista Enlazada, Cola, Pila
├── packet.py              # Clase Packet
├── device.py              # Clases Device e Interface
├── network.py             # Clase Network
├── config_manager.py      # Gestor de configuración
├── cli_parser.py          # Parser CLI
├── requirements.md        # Especificaciones del proyecto
├── README.md             # Este archivo
└── network_config.json   # Configuración guardada (se crea automáticamente)
```

## Características Técnicas

### Paradigma de Programación
- **Programación Orientada a Objetos**: Todas las clases implementan encapsulación, herencia y polimorfismo
- **Patrón Comando**: Cada comando CLI es una clase que implementa la interfaz `Command`

### Validaciones
- Validación de direcciones IP con expresiones regulares
- Verificación de existencia de dispositivos e interfaces
- Validación de argumentos en comandos
- Manejo de errores con mensajes descriptivos

### Persistencia
- Configuraciones guardadas en formato JSON
- Exportación/importación en formato CLI estilo Cisco
- Carga automática de configuración al iniciar

### Datos por Defecto
El simulador incluye una configuración de prueba con:
- Router1 con interfaces g0/0 (192.168.1.1) y g0/1 (10.0.0.1)
- Switch1 con interfaces g0/1 (192.168.1.2) y g0/2 (192.168.1.3)
- PC1 con interfaz eth0 (10.0.0.2)
- PC2 con interfaz eth0 (192.168.1.4)
- Conexiones preestablecidas entre dispositivos

## Ejemplos de Uso

### Envío de Paquetes
```bash
PC1> send 10.0.0.2 192.168.1.4 "Hello, World!" 5
Message queued for delivery.

PC1> tick
[Tick] Procesados: 1, Entregados: 1, Descartados: 0

PC2> show history
Historial de paquetes de PC2:
1) De 10.0.0.2 a 192.168.1.4: "Hello, World!" | TTL al llegar: 3 | Camino: PC1 → Router1 → Switch1 → PC2 | Expirado: No
```

### Configuración de Dispositivos
```bash
Router1> enable
Router1# configure terminal
Router1(config)# interface g0/2
Router1(config-if)# ip address 172.16.0.1
Router1(config-if)# no shutdown
Router1(config-if)# exit
Router1(config)# exit
Router1# show interfaces
Interfaces de Router1:
  g0/0: 192.168.1.1 [up]
  g0/1: 10.0.0.1 [up]
  g0/2: 172.16.0.1 [up]
```

### Guardado y Carga de Configuración
```bash
Router1# save running-config
Configuración CLI exportada a running-config.txt

Router1# load config network.cfg
Configuración CLI importada exitosamente
```

## Evaluación

El proyecto cumple con todos los criterios de evaluación:

1. ✅ **Paradigma de programación orientada a objetos**
2. ✅ **Validaciones de datos introducidos por el usuario**
3. ✅ **Datos guardados como archivos JSON**
4. ✅ **Código comentado correctamente**
5. ✅ **Datos por defecto para pruebas**
6. ✅ **Funcionamiento, legibilidad y aplicación de conceptos en cada módulo**

## Autor

Desarrollado para el curso de Algoritmos y Estructuras de Datos II. 