import pyxel
import time
import random

from src.core.game.entities.Player import Player
from src.core.game.systems.Controller import Controller

class App:
    def __init__(self):
        # Tamanho da janela do jogo
        self.screen_width = 320
        self.screen_height = 240
        
        # Tamanho do mundo (múltiplo de 16)
        self.world_width = 1024  # 64 tiles (1024/16)
        self.world_height = 1024 # 64 tiles (1024/16)
        
        pyxel.init(self.screen_width, self.screen_height, title="RPG Top-Down")
        
        # Carrega a imagem com os sprites
        pyxel.image(0).load(0, 0, "../../../../assets/animations/player/player_characters.png")
        
        # Carrega os tiles (16x16) e cria o mapa
        self.load_tiles()
        
        # Variável global para delta time
        self.dt = 0
        self.last_time = time.time()
        
        # Cria o controlador com as dimensões corretas
        self.controller = Controller(
            screen_width=self.screen_width,
            screen_height=self.screen_height,
            world_width=self.world_width,
            world_height=self.world_height
        )
        
        # Posiciona o jogador no centro do mundo
        player = Player(self.world_width // 2, self.world_height // 2)
        self.controller.set_player(player)
        
        pyxel.run(self.update, self.draw)
    
    def load_tiles(self):
        # Carrega a imagem com os tiles (3 tiles de 16x16)
        pyxel.image(1).load(0, 0, "../../../../assets/tiles/tiles.png")
        
        # Cria um array para armazenar o tipo de cada tile
        self.tile_map = [[0 for _ in range(self.world_width // 16)] 
                        for _ in range(self.world_height // 16)]
        
        # Preenche o mapa com tiles aleatórios (0, 1 ou 2)
        for y in range(len(self.tile_map)):
            for x in range(len(self.tile_map[0])):
                self.tile_map[y][x] = random.randint(0, 2)
    
    def update(self):
        # Calcula o delta time
        current_time = time.time()
        self.dt = current_time - self.last_time
        self.last_time = current_time
        
        # Atualiza o controlador
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
        self.controller.update(self.dt, self.tile_map)
    
    def draw(self):
        self.controller.draw(self.tile_map)