import pyxel
import time

class Camera:
    def __init__(self, width, height):
        self.viewport_width = width
        self.viewport_height = height
        self.x = 0
        self.y = 0
    
    def update(self, target_x, target_y):
        # Centraliza a câmera no jogador
        self.x = target_x - self.viewport_width // 2
        self.y = target_y - self.viewport_height // 2
        
        # Limita a câmera para não sair do mundo
        self.x = max(0, min(self.x, pyxel.width * 64 - self.viewport_width))
        self.y = max(0, min(self.y, pyxel.height * 64 - self.viewport_height))