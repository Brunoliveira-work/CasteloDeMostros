import pyxel

class JoinScreen:
    def __init__(self, game_client):
        self.game_client = game_client
        self.ip_input = ""
        self.port_input = ""
        self.active_input = "ip"
    
    def update(self):
        """Atualiza a tela de join"""
        if pyxel.btnp(pyxel.KEY_TAB):
            self.active_input = "port" if self.active_input == "ip" else "ip"
        
        current_input = self.ip_input if self.active_input == "ip" else self.port_input
        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            current_input = current_input[:-1]
        else:
            for key in range(pyxel.KEY_0, pyxel.KEY_9 + 1):
                if pyxel.btnp(key):
                    current_input += chr(key - pyxel.KEY_0 + ord('0'))
            if pyxel.btnp(pyxel.KEY_PERIOD):
                current_input += "."
        
        if self.active_input == "ip":
            self.ip_input = current_input
        else:
            self.port_input = current_input
        
        if pyxel.btnp(pyxel.KEY_RETURN):
            if self.ip_input and self.port_input:
                try:
                    port = int(self.port_input)
                    self.game_client.join_server(self.ip_input, port)
                except ValueError:
                    pass
        
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            self.game_client.show_menu()
            self.ip_input = ""
            self.port_input = ""
    
    def draw(self):
        """Desenha a tela de join"""
        pyxel.cls(0)  # Limpa a tela
        pyxel.text(100, 50, "Join Game", 7)
        
        label_color = 11 if self.active_input == "ip" else 7
        pyxel.text(50, 100, "IP:", label_color)
        pyxel.rect(80, 100, 150, 10, 1)
        pyxel.text(82, 102, self.ip_input, 7)
        
        label_color = 11 if self.active_input == "port" else 7
        pyxel.text(50, 120, "Port:", label_color)
        pyxel.rect(80, 120, 50, 10, 1)
        pyxel.text(82, 122, self.port_input, 7)
        
        pyxel.text(50, 150, "TAB para alternar entre campos", 8)
        pyxel.text(50, 170, "ENTER para conectar", 8)
        pyxel.text(50, 190, "ESC para voltar", 8)