import pyxel
import time

from src.core.game.entities.Entity import Entity

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 16, 19)
        self.speed = 4
        
        self.sprite_frames = [
            
        ]
        
        with open("../../../../assets/animations/player/knight_sprite.shape", "r") as f:
            for line in f:
                if line.startswith("frame"):
                    parts = line.split()
                    x = int(parts[1])
                    y = int(parts[2])
                    w = int(parts[3])
                    h = int(parts[4])
                    self.sprite_frames.append((x, y, w, h))
                
        self.current_frame = 0
        self.animation_time = 0
        self.animation_speed = 0.2
        self.flip_h = False  # Nova variável para indicar se está invertido
        self.is_moving = False

    def update(self, dt):
        self.is_moving = False

        if pyxel.btn(pyxel.KEY_LEFT):
            self.x -= self.speed
            self.flip_h = True
            self.is_moving = True
        elif pyxel.btn(pyxel.KEY_RIGHT):
            self.x += self.speed
            self.flip_h = False
            self.is_moving = True

        if pyxel.btn(pyxel.KEY_UP):
            self.y -= self.speed
            self.is_moving = True
        elif pyxel.btn(pyxel.KEY_DOWN):
            self.y += self.speed
            self.is_moving = True
    
        # Apenas anima se estiver parado
        if not self.is_moving:
            self.animation_time += dt
            if self.animation_time >= self.animation_speed:
                self.animation_time = 0
                self.current_frame = (self.current_frame + 1) % 2
        else:
            # Se estiver se movendo, anima com os frames de movimento
            self.animation_time += dt
            if self.animation_time >= 0.1:
                self.animation_time = 0
                self.current_frame = ((self.current_frame + 1) % 3) + 3  # Adiciona 2 para os frames de movimento

    def draw(self, camera_x, camera_y):
        frame = self.sprite_frames[self.current_frame]
        pyxel.blt(
            self.x - camera_x - (frame[2] - self.width) // 2,
            self.y - camera_y - (frame[3] - self.height),
            0,
            frame[0],
            frame[1],
            -frame[2] if self.flip_h else frame[2],  # Largura negativa = flip horizontal
            frame[3],
            13
        )