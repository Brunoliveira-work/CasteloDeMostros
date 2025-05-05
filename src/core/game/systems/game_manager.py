import multiprocessing as mp
import time
from dataclasses import dataclass
from typing import List, Dict, Tuple


@dataclass
class GameRenderData:
    # Dados do player
    player_sprite: Tuple[int, int, int, int]  # (u, v, w, h)
    player_pos: Tuple[float, float]
    player_flip: bool
    
    # Dados do mapa
    map_tiles: List[List[Tuple[int, int, int]]]  # Matriz de tiles (tile_x, tile_y, tile_type)
    scroll_x: float
    
    # Dados dos obstáculos
    obstacles: List[Dict]  # Lista de obstáculos com tipo e posição
    
    # Dados do jogo
    score: float
    speed: float
    is_paused: bool

class GameManager:
    def __init__(self):
        self.state_queue = mp.Queue()
        self.input_queue = mp.Queue()
        
        self.game_process = mp.Process(
            target=self._game_loop,
            daemon=True
        )
        self.game_process.start()
    
    def _game_loop(self):
        """Loop principal da lógica do jogo"""
        from core.game.entities.player import Player
        from core.game.levels.map_generator import MapGenerator
        from core.game.systems.obstacle_controller import ObstacleController
        from core.game.entities.obstacle import SkeletonObstacle
        
        # Inicializa sistemas
        map_gen = MapGenerator()
        player = Player(100, map_gen.get_ground_y())
        obstacles = ObstacleController(map_gen.get_ground_y())
        
        last_time = time.time()
        
        while True:
            # Processa inputs
            self._process_inputs(player)
            
            # Atualiza lógica
            current_time = time.time()
            dt = min(current_time - last_time, 0.033)
            last_time = current_time
            
            if not player.is_paused:
                map_gen.update(dt)
                player.update(map_gen.get_ground_y(), dt)
                obstacles.update(dt)
                
                if self._check_collisions(player, obstacles):
                    player.is_paused = True
            
            # Prepara dados para renderização
            render_data = GameRenderData(
                player_sprite=player.get_current_sprite(),
                player_pos=(player.x, player.y),
                player_flip=False,
                map_tiles=map_gen.get_visible_tiles(),
                scroll_x=map_gen.scroll_x,
                obstacles=[{
                    'type': 'skeleton' if isinstance(o, SkeletonObstacle) else 'square',
                    'x': o.x,
                    'y': o.y,
                    'frame': o.current_frame if hasattr(o, 'current_frame') else 0
                } for o in obstacles.obstacles],
                score=player.score,
                speed=player.game_state.speed_multiplier,
                is_paused=player.is_paused
            )
            
            self.state_queue.put(render_data)
    
    def _process_inputs(self, player):
        while not self.input_queue.empty():
            cmd = self.input_queue.get()
            if cmd == "JUMP":
                player.jump()
            elif cmd == "DUCK":
                player.duck(True)
            elif cmd == "STAND":
                player.duck(False)
    
    def _check_collisions(self, player, obstacles):
        for obstacle in obstacles.obstacles:
            if player.check_collision(obstacle):
                return True
        return False
    
    def send_input(self, command: str):
        self.input_queue.put(command)
    
    def get_render_data(self) -> GameRenderData:
        return self.state_queue.get_nowait() if not self.state_queue.empty() else None