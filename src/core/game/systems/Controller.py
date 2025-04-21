import pyxel

from src.core.game.entities.Entity import Entity
from src.core.game.entities.Player import Player
from src.core.game.ui.cam.Camera import Camera
from src.core.game.world.World import World

class Controller:
    def __init__(self, screen_width, screen_height, world_width, world_height):
        self.world = World(world_width, world_height)
        self.camera = Camera(screen_width, screen_height)
        self.player = None
    
    def set_player(self, player):
        self.player = player
        self.world.add_entity(player)
    
    def update(self, dt, tile_map=None):
        self.world.update(dt)
        # Atualiza a câmera para seguir o jogador
        self.camera.update(self.player.x, self.player.y)
    
    def draw(self, tile_map):
        pyxel.cls(0)
        # Desenha o mundo com o offset da câmera
        self.world.draw(self.camera.x, self.camera.y, tile_map)