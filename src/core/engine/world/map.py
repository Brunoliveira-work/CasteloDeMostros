import pyxel
from enum import Enum

class TileType(Enum):
    WALKABLE = 0
    WALL = 1
    WATER = 2

class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = [[TileType.WALKABLE for _ in range(width)] for _ in range(height)]
        self.tile_size = 16
        
    def load_from_tiledata(self, data):
        """Carrega o mapa a partir de dados (pode ser do Pyxel ou arquivo externo)"""
        for y in range(self.height):
            for x in range(self.width):
                self.tiles[y][x] = TileType(data[y][x])
    
    def is_walkable(self, x, y):
        """Verifica se a posição é transitável"""
        tile_x, tile_y = int(x // self.tile_size), int(y // self.tile_size)
        if 0 <= tile_x < self.width and 0 <= tile_y < self.height:
            return self.tiles[tile_y][tile_x] == TileType.WALKABLE
        return False
    
    def check_map_collision(self, collider):
        """Verifica colisão com tiles não walkable"""
        # Para um collider circular
        radius = collider.radius
        
        # Verifica os 4 pontos cardeais + centro
        points_to_check = [
            (collider.x, collider.y),  # centro
            (collider.x - radius, collider.y),  # esquerda
            (collider.x + radius, collider.y),  # direita
            (collider.x, collider.y - radius),  # topo
            (collider.x, collider.y + radius)   # base
        ]
        
        for px, py in points_to_check:
            if not self.is_walkable(px, py):
                return True
        return False