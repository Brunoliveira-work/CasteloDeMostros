import pyxel

class HostLobbyScreen:
    def __init__(self, game_client):
        self.game_client = game_client
    
    def update(self):
        """Atualiza o lobby do host"""
        if pyxel.btnp(pyxel.KEY_RETURN) and self.game_client.network.host:
            self.game_client.network.start_game()
            self.game_client.current_screen = "game"
    
    def draw(self):
        """Desenha o lobby do host"""
        pyxel.cls(0)  # Limpa a tela
        pyxel.text(100, 30, "Host Lobby", 7)
        pyxel.text(50, 60, f"IP: {self.game_client.network.client_ip}", 7)
        pyxel.text(50, 80, f"Port: {self.game_client.network.server_port}", 7)
        
        pyxel.text(50, 110, "Players:", 7)
        y = 130
        for player_id, info in self.game_client.network.clients.items():
            pyxel.text(70, y, f"ID: {player_id} - IP: {info['ip']}", 7)
            y += 20
        
        if self.game_client.network.host:
            pyxel.text(50, 200, "Pressione ENTER para iniciar o jogo", 11)
        else:
            pyxel.text(50, 200, "Aguardando host iniciar o jogo...", 8)