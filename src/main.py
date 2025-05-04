import pyxel
import time
from core.game.entities.player import Player
from core.game.levels.map_generator import MapGenerator
from core.game.systems.game_state import GameState
from core.game.systems.obstacle_controller import ObstacleController
from core.game.entities.obstacle import Obstacle

class MainGame:
    def __init__(self):
        self.screen_width = 320
        self.screen_height = 240
        self.is_paused = False
        pyxel.init(self.screen_width, self.screen_height, title="Dino Multiplayer Clone", fps=60)
        
        # Carrega os assets
        pyxel.image(0).load(0, 0, "../assets/animations/player/banco_0.png")
        pyxel.image(1).load(0, 0, "../assets/animations/player/castle-tileset.png")
        
        # Inicializa o estado do jogo
        self.game_state = GameState()
        
        # Passa game_state para os outros sistemas
        self.map = MapGenerator(self.game_state)
        self.player = Player(100, self.map.get_ground_y(), self.game_state)
        
        self.score = 0
        self.last_time = time.time()
        self.last_speed_increase = time.time()
        
        self.obstacle_controller = ObstacleController(
            self.game_state,
            self.map.get_ground_y()
        )
        
        pyxel.run(self.update, self.draw)
        
        pyxel.run(self.update, self.draw)
    
    def update(self):
        if self.is_paused:
            return  # Não atualiza nada se o jogo está pausado
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        
        # Aumenta a velocidade gradualmente a cada 10 segundos
        # if current_time - self.last_speed_increase > 10:
        #     self.game_state.increase_speed(0.05)
        #     self.last_speed_increase = current_time
        
        # Atualiza sistemas com delta time ajustado pela velocidade
         # Limita o dt para evitar saltos grandes
        dt = min(dt, 0.033)  # ~30 FPS mínimo
        
        # Atualiza sistemas
        adjusted_dt = dt * self.game_state.speed_multiplier
        self.map.update(adjusted_dt)
        self.player.update(self.map.get_ground_y(), adjusted_dt)
        self.obstacle_controller.update(adjusted_dt)
         # Verifica colisões
        self.check_collisions()
        # Atualiza pontuação
        self.score += 2 * dt * self.game_state.speed_multiplier
    
    def draw(self):
        pyxel.cls(7)
        self.map.draw(pyxel.width, pyxel.height)
        self.obstacle_controller.draw()
        self.player.draw()
        
        # Mostra velocidade atual
        pyxel.text(10, 10, f"SCORE: {int(self.score)}", 0)
        pyxel.text(10, 20, f"SPEED: {self.game_state.speed_multiplier:.1f}x", 0)
        # Mostra mensagem de pausa se colidiu
        if self.is_paused:
            pyxel.text(self.screen_width//2 - 30, self.screen_height//2, "GAME OVER", pyxel.COLOR_RED)
    
    def check_collisions(self):
        """Verifica colisões entre player e obstáculos"""
        for obstacle in self.obstacle_controller.obstacles:
            if self.player.check_collision(obstacle):
                self.game_paused()
                break
    
    def game_paused(self):
        """Pausa o jogo quando ocorre colisão"""
        self.is_paused = True
        print("Jogo pausado devido a colisão!")  # Você pode substituir por uma mensagem na tela
    
MainGame()