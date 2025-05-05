import socket
import threading
from typing import Dict

class NetworkManager:
    def __init__(self):
        self.host = False
        self.connected = False
        self.server_ip = ""
        self.server_port = 0
        self.client_ip = ""
        self.player_id = ""
        self.clients: Dict[str, Dict] = {}  # {id: {"ip": str, "port": int}}
        self.socket = None
        self.receive_thread = None

    def start_host(self, server_ip: str, server_port: int):
        """Configura como host"""
        self.host = True
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_ip = self._get_local_ip()
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.client_ip, 0))  # Porta aleatória
        
        self.receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
        self.receive_thread.start()
    
    def join_server(self, ip: str, port: int):
        """Conecta a um servidor"""
        self.host = False
        self.server_ip = ip
        self.server_port = port
        self.client_ip = self._get_local_ip()
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.client_ip, 0))  # Porta aleatória
        
        self._send_message("JOIN")
        
        self.receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
        self.receive_thread.start()
    
    def _get_local_ip(self):
        """Obtém o IP local"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip
    
    def _send_message(self, message: str):
        """Envia mensagem para o servidor"""
        if self.socket:
            self.socket.sendto(message.encode(), (self.server_ip, self.server_port))
    
    def _receive_messages(self):
        """Thread para receber mensagens"""
        while True:
            try:
                data, addr = self.socket.recvfrom(1024)
                message = data.decode()
                
                if message.startswith("ID:"):
                    self.player_id = message[3:]  # This should be like "player_1"
                    print(f"Received player ID: {self.player_id}")
                elif message.startswith("PLAYER_LIST:"):
                    self._update_player_list(message[12:])
                elif message == "START_GAME":
                    self.connected = True
                    
            except Exception as e:
                print(f"Erro ao receber mensagem: {e}")
                break
    
    def _update_player_list(self, players_data: str):
        """Atualiza lista de jogadores"""
        self.clients = {}
        if players_data:
            for player_info in players_data.split(";"):
                if player_info:
                    player_id, ip, port = player_info.split(",")
                    self.clients[player_id] = {"ip": ip, "port": int(port)}
    
    def start_game(self):
        """Envia comando para iniciar o jogo (apenas host)"""
        if self.host:
            self._send_message("START_GAME")
            self.connected = True
    
    def close(self):
        """Fecha a conexão"""
        if self.socket:
            self.socket.close()
        if self.receive_thread:
            self.receive_thread.join(0.1)