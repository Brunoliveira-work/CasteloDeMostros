from typing import Dict
import pyxel

class GameStateServer:
    def __init__(self):
        self.players: Dict[str, Dict] = {}
        self.obstacles = []
        self.score = 0
        self.is_paused = False
        self.tile_size = 16
        self.scroll_x = 0
        self.screen_width = 320
        self.screen_height = 240
        self.speed_multiplier = 1.0  # Add this line
        self.next_player_id = 1

    def add_player(self) -> str:
        """Add a new player and return their ID"""
        player_id = f"player_{self.next_player_id}"
        self.next_player_id += 1
        
        self.players[player_id] = {
            'x': 50,
            'y': 10 * self.tile_size,
            'width': 16,
            'height': 32,
            'duck_height': 16,
            'is_ducking': False,
            'color': self._get_player_color(self.next_player_id - 1)
        }
        return player_id

    def _get_player_color(self, player_index: int) -> int:
        """Return a unique color for each player"""
        colors = [
            pyxel.COLOR_RED,
            pyxel.COLOR_GREEN,
            pyxel.COLOR_YELLOW
        ]
        return colors[player_index % len(colors)]

    def update_player_action(self, player_id: str, action: str, value: bool):
        """Update player action state"""
        if player_id in self.players:
            if action == 'jump':
                # Implement jump logic here
                pass
            elif action == 'duck':
                self.players[player_id]['is_ducking'] = value

    def update(self, dt: float):
        """Update game state"""
        if not self.is_paused:
            self.scroll_x += 2 * self.speed_multiplier
            self.score += 1 * self.speed_multiplier
            
            # Gradually increase difficulty
            if self.score % 500 == 0:
                self.speed_multiplier = min(self.speed_multiplier + 0.1, 3.0)

    def get_game_state(self) -> Dict:
        """Return current game state"""
        return {
            'players': self.players,
            'obstacles': self.obstacles,
            'score': self.score,
            'is_paused': self.is_paused,
            'scroll_x': self.scroll_x,
            'tile_size': self.tile_size,
            'screen_width': self.screen_width,
            'screen_height': self.screen_height,
            'speed_multiplier': self.speed_multiplier,  # Include this
            'background_tiles': self._get_background_tiles(),
            'ground_tiles': self._get_ground_tiles()
        }

    def _get_background_tiles(self):
        """Generate background tiles"""
        return [(x, y, 0) for x in range(0, 100) for y in range(10, 12)]

    def _get_ground_tiles(self):
        """Generate ground tiles"""
        return [(x, 12, 1) for x in range(0, 100)]