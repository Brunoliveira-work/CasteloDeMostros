import pyxel
import multiprocessing as mp
from typing import Dict
from core.game.systems.game_server import GameServer
from core.game.systems.network_manager import NetworkManager
from core.game.ui.screens.menu_screen import MenuScreen
from core.game.ui.screens.join_screen import JoinScreen
from core.game.ui.screens.host_lobby_screen import HostLobbyScreen
from core.game.ui.screens.game_screen import GameScreen
from core.game.systems.game_state_server import GameStateServer

class GameClient:
    def __init__(self):
        self.network = NetworkManager()
        self.network_server = GameServer()
        self.game_state_server = GameStateServer()
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
        self._initialize_pyxel()
        pyxel.run(self.update, self.draw)

    def _initialize_pyxel(self):
        """Initialize Pyxel resources"""
        pyxel.init(320, 240, title="Castelo de Monstros", fps=60)
        pyxel.image(0).load(0, 0, "../assets/animations/player/banco_0.png")
        pyxel.image(1).load(0, 0, "../assets/animations/player/castle-tileset.png")

    # Screen transition methods
    def show_menu(self):
        """Return to main menu"""
        self.current_screen = "menu"
        if self.network.host:
            self.network_server.stop()
        self.network.close()

    def show_join_screen(self):
        """Show the join server screen"""
        self.current_screen = "join"

    def show_host_lobby(self):
        """Show the host lobby screen"""
        self.current_screen = "host_lobby"

    def show_game_screen(self):
        """Show the game screen"""
        self.current_screen = "game"

    def start_host(self):
        """Start hosting a game"""
        ip, port = self.network_server.start()
        self.network.start_host(ip, port)
        self.player_id = self.game_state_server.add_player()
        self.show_host_lobby()

    def join_server(self, ip: str, port: int):
        """Join an existing game server"""
        self.network.join_server(ip, port)
        self.player_id = self.game_state_server.add_player()
        self.show_host_lobby()

    def start_game(self):
        """Start the game (host only)"""
        if self.network.host:
            self.network.start_game()
            self.show_game_screen()

    def update(self):
        """Update current screen"""
        self.screens[self.current_screen].update()

    def draw(self):
        """Draw current screen"""
        self.screens[self.current_screen].draw()

    def close(self):
        """Cleanup resources"""
        if self.network.host:
            self.network_server.stop()
        self.network.close()
        pyxel.quit()

def main():
    client = GameClient()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        client.close()

if __name__ == "__main__":
    # Required for multiprocessing on Windows
    mp.freeze_support()
    main()