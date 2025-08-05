"""
Parser CLI para el Simulador de Red
Maneja múltiples niveles de contexto y comandos estilo Cisco
"""

import re
from abc import ABC, abstractmethod

class Command(ABC):
    """Clase abstracta para comandos (Patrón Comando)"""
    
    @abstractmethod
    def execute(self, network, args):
        """Ejecuta el comando"""
        pass

class EnableCommand(Command):
    """Comando enable - eleva al modo privilegiado"""
    def execute(self, network, args):
        return "Modo privilegiado habilitado", "privileged"

class DisableCommand(Command):
    """Comando disable - regresa al modo usuario"""
    def execute(self, network, args):
        return "Modo privilegiado deshabilitado", "user"

class ConfigureTerminalCommand(Command):
    """Comando configure terminal - entra al modo configuración"""
    def execute(self, network, args):
        return "Entrando al modo configuración global", "config"

class HostnameCommand(Command):
    """Comando hostname - establece el nombre del dispositivo"""
    def execute(self, network, args):
        if len(args) < 1:
            return "Error: Se requiere un nombre de dispositivo", None
        
        new_name = args[0]
        if network.current_device:
            old_name = network.current_device.name
            network.current_device.name = new_name
            # Actualizar en el diccionario de dispositivos
            if old_name in network.devices:
                network.devices[new_name] = network.devices.pop(old_name)
            return f"Nombre del dispositivo cambiado a {new_name}", None
        return "Error: No hay dispositivo actual", None

class InterfaceCommand(Command):
    """Comando interface - entra al modo configuración de interfaz"""
    def execute(self, network, args):
        if len(args) < 1:
            return "Error: Se requiere un nombre de interfaz", None
        
        interface_name = args[0]
        if network.current_device:
            if interface_name not in network.current_device.interfaces:
                network.current_device.add_interface(interface_name)
            # Establecer la interfaz actual
            network.current_device.current_interface = network.current_device.get_interface(interface_name)
            return f"Entrando al modo configuración de interfaz {interface_name}", "interface"
        return "Error: No hay dispositivo actual", None

class IpAddressCommand(Command):
    """Comando ip address - establece la dirección IP de la interfaz"""
    def execute(self, network, args):
        if len(args) < 1:
            return "Error: Se requiere una dirección IP", None
        
        ip_address = args[0]
        # Validación básica de IP
        if not re.match(r'^\d+\.\d+\.\d+\.\d+$', ip_address):
            return "Error: Formato de IP inválido", None
        
        if network.current_device and hasattr(network.current_device, 'current_interface') and network.current_device.current_interface:
            network.current_device.current_interface.set_ip_address(ip_address)
            return f"Dirección IP {ip_address} configurada", None
        return "Error: No hay interfaz seleccionada", None

class ShutdownCommand(Command):
    """Comando shutdown - desactiva la interfaz"""
    def execute(self, network, args):
        if network.current_device and hasattr(network.current_device, 'current_interface') and network.current_device.current_interface:
            network.current_device.current_interface.shutdown()
            return "Interfaz desactivada", None
        return "Error: No hay interfaz seleccionada", None

class NoShutdownCommand(Command):
    """Comando no shutdown - activa la interfaz"""
    def execute(self, network, args):
        if network.current_device and hasattr(network.current_device, 'current_interface') and network.current_device.current_interface:
            network.current_device.current_interface.no_shutdown()
            return "Interfaz activada", None
        return "Error: No hay interfaz seleccionada", None

class ExitCommand(Command):
    """Comando exit - sale del modo actual"""
    def execute(self, network, args):
        if network.current_device and hasattr(network.current_device, 'current_interface') and network.current_device.current_interface:
            network.current_device.current_interface = None
            return "Saliendo del modo configuración de interfaz", "config"
        elif network.current_device:
            return "Saliendo del modo configuración global", "privileged"
        return "Saliendo del modo privilegiado", "user"

class EndCommand(Command):
    """Comando end - regresa al modo privilegiado desde cualquier modo"""
    def execute(self, network, args):
        if network.current_device and hasattr(network.current_device, 'current_interface'):
            network.current_device.current_interface = None
        return "Regresando al modo privilegiado", "privileged"

class ConnectCommand(Command):
    """Comando connect - conecta dos interfaces"""
    def execute(self, network, args):
        if len(args) < 4:
            return "Error: Se requieren 4 argumentos: <iface1> <device2> <iface2>", None
        
        interface1_name, device2_name, interface2_name = args[0], args[1], args[2]
        device1_name = network.current_device.name if network.current_device else None
        
        if not device1_name:
            return "Error: No hay dispositivo actual", None
        
        success, message = network.connect_interfaces(
            device1_name, interface1_name, device2_name, interface2_name
        )
        return message, None

class DisconnectCommand(Command):
    """Comando disconnect - desconecta dos interfaces"""
    def execute(self, network, args):
        if len(args) < 4:
            return "Error: Se requieren 4 argumentos: <iface1> <device2> <iface2>", None
        
        interface1_name, device2_name, interface2_name = args[0], args[1], args[2]
        device1_name = network.current_device.name if network.current_device else None
        
        if not device1_name:
            return "Error: No hay dispositivo actual", None
        
        success, message = network.disconnect_interfaces(
            device1_name, interface1_name, device2_name, interface2_name
        )
        return message, None

class SendCommand(Command):
    """Comando send - envía un paquete"""
    def execute(self, network, args):
        if len(args) < 3:
            return "Error: Se requieren al menos 3 argumentos: <source_ip> <destination_ip> <message> [ttl]", None
        
        source_ip = args[0]
        destination_ip = args[1]
        message = args[2]
        ttl = int(args[3]) if len(args) > 3 else 10
        
        success, message_result = network.send_packet(source_ip, destination_ip, message, ttl)
        return message_result, None

class TickCommand(Command):
    """Comando tick/process - procesa paquetes en la red"""
    def execute(self, network, args):
        result = network.process_packets()
        return (f"[Tick] Procesados: {result['processed']}, "
                f"Entregados: {result['delivered']}, "
                f"Descartados: {result['dropped']}"), None

class ShowCommand(Command):
    """Comando show - muestra información"""
    def execute(self, network, args):
        if len(args) < 1:
            return "Error: Se requiere un subcomando para show", None
        
        subcommand = args[0].lower()
        
        if subcommand == "interfaces":
            return self._show_interfaces(network)
        elif subcommand == "history":
            return self._show_history(network, args[1:] if len(args) > 1 else [])
        elif subcommand == "queue":
            return self._show_queue(network, args[1:] if len(args) > 1 else [])
        elif subcommand == "statistics":
            return self._show_statistics(network)
        elif subcommand == "devices":
            return self._show_devices(network)
        else:
            return f"Error: Subcomando '{subcommand}' no reconocido", None
    
    def _show_interfaces(self, network):
        """Muestra información de interfaces"""
        if not network.current_device:
            return "Error: No hay dispositivo actual", None
        
        result = [f"Interfaces de {network.current_device.name}:"]
        for interface_name, interface in network.current_device.interfaces.items():
            status = "up" if interface.is_up() else "down"
            ip = interface.ip_address or "sin IP"
            result.append(f"  {interface_name}: {ip} [{status}]")
        
        return "\n".join(result), None
    
    def _show_history(self, network, args):
        """Muestra historial de paquetes"""
        device_name = args[0] if args else None
        device = network.get_device(device_name) if device_name else network.current_device
        
        if not device:
            return "Error: Dispositivo no encontrado", None
        
        history = device.get_history()
        if not history:
            return f"No hay historial de paquetes en {device.name}", None
        
        result = [f"Historial de paquetes de {device.name}:"]
        for i, packet_info in enumerate(history, 1):
            expired = "Sí" if packet_info["expired"] else "No"
            result.append(f"{i}) De {packet_info['source_ip']} a {packet_info['destination_ip']}: "
                         f"\"{packet_info['message']}\" | TTL al llegar: {packet_info['ttl_at_arrival']} | "
                         f"Camino: {packet_info['path']} | Expirado: {expired}")
        
        return "\n".join(result), None
    
    def _show_queue(self, network, args):
        """Muestra colas de paquetes"""
        device_name = args[0] if args else None
        device = network.get_device(device_name) if device_name else network.current_device
        
        if not device:
            return "Error: Dispositivo no encontrado", None
        
        result = [f"Colas de paquetes de {device.name}:"]
        for interface_name, interface in device.interfaces.items():
            input_size = interface.get_input_queue_size()
            output_size = interface.get_output_queue_size()
            result.append(f"  {interface_name}: entrada={input_size}, salida={output_size}")
        
        return "\n".join(result), None
    
    def _show_statistics(self, network):
        """Muestra estadísticas de la red"""
        stats = network.get_network_statistics()
        result = [
            "Estadísticas de la red:",
            f"Total de dispositivos: {stats['total_devices']}",
            f"Dispositivos en línea: {stats['online_devices']}",
            f"Total de conexiones: {stats['total_connections']}",
            f"Paquetes enviados: {stats['total_packets_sent']}",
            f"Paquetes entregados: {stats['total_packets_delivered']}",
            f"Paquetes descartados: {stats['total_packets_dropped']}",
            f"Promedio de saltos por paquete: {stats['average_hops_per_packet']}"
        ]
        return "\n".join(result), None
    
    def _show_devices(self, network):
        """Muestra lista de dispositivos"""
        result = ["Dispositivos en la red:"]
        for device in network.devices.values():
            status_icon = "✓" if device.is_online() else "✗"
            result.append(f"  - {device.name} ({device.type}) [{status_icon}]")
        return "\n".join(result), None

class SaveCommand(Command):
    """Comando save - guarda configuración"""
    def execute(self, network, args):
        filename = args[0] if args else "running-config.txt"
        success, message = network.config_manager.export_cli_config(network, filename)
        return message, None

class LoadCommand(Command):
    """Comando load - carga configuración"""
    def execute(self, network, args):
        if len(args) < 2 or args[0] != "config":
            return "Error: Uso: load config <filename>", None
        
        filename = args[1]
        success, message = network.config_manager.import_cli_config(network, filename)
        return message, None

class SetDeviceStatusCommand(Command):
    """Comando set_device_status - cambia estado de dispositivo"""
    def execute(self, network, args):
        if len(args) < 2:
            return "Error: Se requieren 2 argumentos: <device> <online|offline>", None
        
        device_name = args[0]
        status = args[1].lower()
        
        if status not in ["online", "offline"]:
            return "Error: Estado debe ser 'online' u 'offline'", None
        
        device = network.get_device(device_name)
        if not device:
            return f"Error: Dispositivo '{device_name}' no encontrado", None
        
        device.set_status(status)
        return f"Estado de {device_name} cambiado a {status}", None

class ListDevicesCommand(Command):
    """Comando list_devices - lista dispositivos"""
    def execute(self, network, args):
        result = ["Dispositivos en la red:"]
        for device in network.devices.values():
            status = "online" if device.is_online() else "offline"
            result.append(f"  - {device.name} ({status})")
        return "\n".join(result), None

class HelpCommand(Command):
    """Comando help - muestra ayuda"""
    def execute(self, network, args):
        help_text = """
Comandos disponibles:

Modo Usuario:
  enable                    - Entra al modo privilegiado
  show devices             - Lista dispositivos
  show interfaces          - Muestra interfaces del dispositivo actual
  show history [device]    - Muestra historial de paquetes
  show queue [device]      - Muestra colas de paquetes
  show statistics          - Muestra estadísticas de la red
  send <src_ip> <dst_ip> <msg> [ttl] - Envía un paquete
  tick                     - Procesa paquetes en la red
  list_devices             - Lista todos los dispositivos
  set_device_status <dev> <online|offline> - Cambia estado de dispositivo
  help                     - Muestra esta ayuda
  exit                     - Sale del simulador

Modo Privilegiado:
  configure terminal       - Entra al modo configuración
  connect <if1> <dev2> <if2> - Conecta interfaces
  disconnect <if1> <dev2> <if2> - Desconecta interfaces
  disable                  - Regresa al modo usuario
  end                      - Regresa al modo privilegiado desde cualquier modo

Modo Configuración:
  hostname <name>          - Cambia nombre del dispositivo
  interface <name>         - Entra al modo configuración de interfaz
  exit                     - Regresa al modo privilegiado
  end                      - Regresa al modo privilegiado

Modo Configuración de Interfaz:
  ip address <ip>          - Establece dirección IP
  shutdown                 - Desactiva interfaz
  no shutdown              - Activa interfaz
  exit                     - Regresa al modo configuración

Configuración:
  save running-config      - Guarda configuración en archivo
  load config <filename>   - Carga configuración desde archivo
        """
        return help_text, None

class CLIParser:
    """Parser principal para la interfaz de línea de comandos"""
    
    def __init__(self, network, config_manager):
        """Inicializa el parser CLI"""
        self.network = network
        self.config_manager = config_manager
        self.mode = "user"  # user, privileged, config, interface
        self.commands = self._initialize_commands()
    
    def _initialize_commands(self):
        """Inicializa todos los comandos disponibles"""
        return {
            "enable": EnableCommand(),
            "disable": DisableCommand(),
            "configure": self._configure_handler,
            "hostname": HostnameCommand(),
            "interface": InterfaceCommand(),
            "ip": self._ip_handler,
            "shutdown": ShutdownCommand(),
            "no": self._no_handler,
            "exit": ExitCommand(),
            "end": EndCommand(),
            "connect": ConnectCommand(),
            "disconnect": DisconnectCommand(),
            "send": SendCommand(),
            "tick": TickCommand(),
            "process": TickCommand(),  # Alias para tick
            "show": ShowCommand(),
            "save": SaveCommand(),
            "load": LoadCommand(),
            "set_device_status": SetDeviceStatusCommand(),
            "list_devices": ListDevicesCommand(),
            "help": HelpCommand(),
            "?": HelpCommand()
        }
    
    def _configure_handler(self, network, args):
        """Maneja el comando configure"""
        if args and args[0].lower() == "terminal":
            return "Entrando al modo configuración global", "config"
        return "Error: Uso: configure terminal", None
    
    def _ip_handler(self, network, args):
        """Maneja comandos ip"""
        if args and args[0].lower() == "address":
            # Verificar que estamos en modo interfaz
            if self.mode != "interface" or not network.current_device or not hasattr(network.current_device, 'current_interface'):
                return "Error: Debe estar en modo configuración de interfaz", None
            return IpAddressCommand().execute(network, args[1:])
        return "Error: Comando ip no reconocido", None
    
    def _no_handler(self, network, args):
        """Maneja comandos no"""
        if args and args[0].lower() == "shutdown":
            # Verificar que estamos en modo interfaz
            if self.mode != "interface" or not network.current_device or not hasattr(network.current_device, 'current_interface'):
                return "Error: Debe estar en modo configuración de interfaz", None
            return NoShutdownCommand().execute(network, args[1:])
        return "Error: Comando no no reconocido", None
    
    def parse_command(self, command_line):
        """Parsea y ejecuta un comando"""
        if not command_line.strip():
            return None
        
        # Dividir el comando en partes
        parts = command_line.strip().split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Verificar si el comando existe
        if command not in self.commands:
            return f"Error: Comando '{command}' no reconocido. Escriba 'help' para ver comandos disponibles."
        
        # Verificar permisos según el modo
        if not self._check_permissions(command):
            return f"Error: Comando '{command}' no disponible en modo {self.mode}"
        
        # Ejecutar el comando
        try:
            cmd_handler = self.commands[command]
            if hasattr(cmd_handler, 'execute'):
                result, new_mode = cmd_handler.execute(self.network, args)
                if new_mode:
                    self.mode = new_mode
                return result
            else:
                # Para comandos especiales como configure, ip, no
                result, new_mode = cmd_handler(self.network, args)
                if new_mode:
                    self.mode = new_mode
                return result
        except Exception as e:
            return f"Error al ejecutar comando: {e}"
    
    def _check_permissions(self, command):
        """Verifica si un comando está permitido en el modo actual"""
        user_commands = {"enable", "show", "send", "tick", "process", "list_devices", 
                        "set_device_status", "help", "?", "exit"}
        privileged_commands = {"configure", "connect", "disconnect", "disable", "end"}
        config_commands = {"hostname", "interface", "exit", "end"}
        interface_commands = {"ip", "shutdown", "no", "exit"}
        
        if self.mode == "user":
            return command in user_commands
        elif self.mode == "privileged":
            return command in user_commands or command in privileged_commands
        elif self.mode == "config":
            return command in user_commands or command in privileged_commands or command in config_commands
        elif self.mode == "interface":
            return command in user_commands or command in privileged_commands or command in config_commands or command in interface_commands
        
        return False
    
    def get_prompt(self):
        """Retorna el prompt actual según el modo"""
        if not self.network.current_device:
            return "Network> "
        
        device_name = self.network.current_device.name
        
        if self.mode == "user":
            return f"{device_name}> "
        elif self.mode == "privileged":
            return f"{device_name}# "
        elif self.mode == "config":
            return f"{device_name}(config)# "
        elif self.mode == "interface":
            return f"{device_name}(config-if)# "
        
        return f"{device_name}> " 