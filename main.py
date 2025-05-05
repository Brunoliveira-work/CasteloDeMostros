import pyxel
from src.core.game.systems.network_manager import NetworkManager
from src.core.game.systems.game_server import GameStateServer
from src.core.game.ui.screens.menu_screen import MenuScreen
from src.core.game.ui.screens.join_screen import JoinScreen
from src.core.game.ui.screens.host_lobby_screen import HostLobbyScreen
from src.core.game.ui.screens.game_screen import GameScreen

class GameClient:
    def __init__(self):
        self.network = NetworkManager()
        self.server = GameStateServer()
        self.player_id = None
        
        # Initialize screens
        self.screens = {
            "menu": MenuScreen(self),
            "join": JoinScreen(self),
            "host_lobby": HostLobbyScreen(self),
            "game": GameScreen(self)
        }
        self.current_screen = "menu"
        
        # Setup Pyxel
        pyxel.init(320, 240, title="Castelo de Monstros", fps=60)
        pyxel.image(0).load(0, 0, "./assets/animations/player/banco_0.png")
        pyxel.image(1).load(0, 0, "./assets/animations/player/castle-tileset.png")
        pyxel.run(self.update, self.draw)
    
    def update(self):
        """Delegates update to current screen"""
        self.screens[self.current_screen].update()
    
    def draw(self):
        """Delegates draw to current screen"""
        self.screens[self.current_screen].draw()
    
    # Screen transition methods
    def show_menu(self):
        self.current_screen = "menu"
    
    def show_join_screen(self):
        self.current_screen = "join"
    
    def start_host(self):
        ip, port = self.network.start_host()
        self.player_id = self.server.add_player()
        self.current_screen = "host_lobby"
    
    def join_server(self, ip: str, port: int):
        self.network.join_server(ip, port)
        self.player_id = self.server.add_player()
        self.current_screen = "host_lobby"

if __name__ == "__main__":
    client = GameClient()