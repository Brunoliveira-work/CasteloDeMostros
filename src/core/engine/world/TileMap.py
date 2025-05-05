import pyxel
import random
from enum import Enum

class TileType(Enum):
    WALKABLE = 0
    WALL = 1
    WATER = 2

class TileMap:
    def __init__(self, world_width, world_height, tile_size=16):
        self.width = world_width // tile_size
        self.height = world_height // tile_size
        self.tile_size = tile_size
        self.tiles = [[TileType.WALKABLE for _ in range(self.width)] 
                     for _ in range(self.height)]
    
    def load_tiles(self):
        """Gera um mapa aleatório"""
        for y in range(self.height):
            for x in range(self.width):
                rand = random.random()
                if rand < 0.2:
                    self.tiles[y][x] = TileType.WALL
                elif rand < 0.3:
                    self.tiles[y][x] = TileType.WATER
    
    def _create_fallback_map(self):
        """Cria mapa vazio para fallback"""
        self.tiles = [[TileType.WALKABLE for _ in range(self.width)] 
                     for _ in range(self.height)]
    
    def is_walkable(self, x, y):
        """Verifica se uma posição é transitável"""
        tile_x, tile_y = int(x // self.tile_size), int(y // self.tile_size)
        if 0 <= tile_x < self.width and 0 <= tile_y < self.height:
            return self.tiles[tile_y][tile_x] == TileType.WALKABLE
        return False
    
    def check_map_collision(self, collider):
        """Verifica colisão com tiles sólidos"""
        points = [
            (collider.x, collider.y),  # Centro
            (collider.x - collider.radius, collider.y),  # Esquerda
            (collider.x + collider.radius, collider.y),  # Direita
            (collider.x, collider.y - collider.radius),  # Topo
            (collider.x, collider.y + collider.radius)   # Base
        ]
        
        return any(not self.is_walkable(x, y) for x, y in points)
    
    def render(self, camera_x, camera_y):
        """Renderiza o mapa visível"""
        start_x = max(0, camera_x // self.tile_size)
        start_y = max(0, camera_y // self.tile_size)
        end_x = min(self.width, (camera_x + pyxel.width) // self.tile_size + 1)
        end_y = min(self.height, (camera_y + pyxel.height) // self.tile_size + 1)
        
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_type = self.tiles[y][x]
                screen_x = x * self.tile_size - camera_x
                screen_y = y * self.tile_size - camera_y
                
                pyxel.blt(
                    screen_x, screen_y,
                    1,  # Banco de imagem
                    tile_type.value * self.tile_size, 0,
                    self.tile_size, self.tile_size,
                    pyxel.COLOR_BLACK
                )