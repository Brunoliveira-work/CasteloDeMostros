import pyxel

class Obstacle:
    def __init__(self, x, y, game_state):
        self.x = x
        self.y = y
        self.width = 15
        self.height = 15
        self.game_state = game_state
        self.color = pyxel.COLOR_WHITE
    
    def update(self, dt):
        """Atualiza posição do obstáculo com base na velocidade do jogo"""
        self.x -= self.game_state.current_speed * dt *60  # Movimento sincronizado com o mapa
    
    def draw(self):
        """Desenha o obstáculo como um quadrado branco"""
        pyxel.rect(self.x, self.y, self.width, self.height, self.color)
    
    def is_off_screen(self, screen_width):
        """Verifica se o obstáculo saiu da tela"""
        return self.x + self.width < 0
    
    def get_hitbox(self):
        """Retorna a hitbox do obstáculo"""
        return (self.x, self.y, self.width, self.height)
    

class SkeletonObstacle:
    def __init__(self, x, y, game_state):
        self.width = 10
        self.height = 14
        self.x = x
        self.y = y - self.height
        self.game_state = game_state
        self.color_key = pyxel.COLOR_GREEN
        
        # Animação
        self.animation_frames = []
        self.current_frame = 0
        self.animation_time = 0
        self.animation_speed = 0.2  # Velocidade da animação
        
        # Carrega os sprites
        self._load_sprites()
    
    def _load_sprites(self):
        """Carrega os frames de animação do arquivo .shape"""
        try:
            with open("../assets/animations/obstacles/skeleton.shape", "r") as f:
                for line in f:
                    if line.startswith("frame"):
                        parts = line.split()
                        x = int(parts[1])
                        y = int(parts[2])
                        w = int(parts[3])
                        h = int(parts[4])
                        self.animation_frames.append((x, y, w, h))
        except FileNotFoundError:
            # Fallback caso o arquivo não exista
            self.animation_frames = [
                (0, 0, 16, 24),  # Frame 1
                (16, 0, 16, 24)  # Frame 2
            ]
            print("Arquivo skeleton.shape não encontrado, usando frames padrão")
    
    def update(self, dt):
        """Atualiza a posição e animação do esqueleto"""
        # Movimento
        self.x -= self.game_state.current_speed * dt * 60
        
        # Animação
        self.animation_time += dt
        if self.animation_time >= self.animation_speed:
            self.animation_time = 0
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
    
    def draw(self):
        """Desenha o esqueleto com a animação atual"""
        frame = self.animation_frames[self.current_frame]
        pyxel.blt(
            self.x,
            self.y + self.height - frame[3],  # Ajusta a posição Y
            0,  # Banco de imagens
            frame[0], frame[1],  # u, v
            frame[2], frame[3],  # w, h
            self.color_key
        )
    
    def get_hitbox(self):
        """Retorna a hitbox do obstáculo para colisão"""
        return (self.x, self.y, self.width, self.height)
    
    def is_off_screen(self, screen_width):
        """Verifica se o obstáculo saiu da tela"""
        return self.x + self.width < 0
    

class ObstacleRenderer:
    def __init__(self, image_bank: int = 1):
        self.image_bank = image_bank
    
    def draw(self, obstacle_data: dict, scroll_x: float):
        adjusted_x = obstacle_data['x'] - scroll_x
        pyxel.blt(
            adjusted_x, obstacle_data['y'],
            self.image_bank,
            *obstacle_data['current_frame'],
            pyxel.COLOR_GREEN
        )