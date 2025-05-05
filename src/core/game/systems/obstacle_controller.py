import random
import pyxel
from core.game.entities.obstacle import Obstacle
from core.game.entities.obstacle import SkeletonObstacle

class ObstacleController:
    def __init__(self, game_state, ground_y):
        self.game_state = game_state
        self.ground_y = ground_y
        self.obstacles = []
        self.spawn_timer = 0
        self.spawn_interval = 2.5  # Segundos entre obstáculos
        self.obstacle_height = 24  # Altura do esqueleto
        
        # Probabilidades de spawn
        self.obstacle_types = [
            (1, "skeleton") # 30% de chance de esqueleto
        ]
    
    def update(self, dt):
        """Atualiza obstáculos existentes e gera novos"""
        # Atualiza obstáculos
        for obstacle in self.obstacles[:]:
            obstacle.update(dt)
            if obstacle.is_off_screen(pyxel.width):
                self.obstacles.remove(obstacle)
        
        adjusted_spawn_interval = self.spawn_interval / (self.game_state.speed_multiplier ** 0.8)
    
        self.spawn_timer += dt
        if self.spawn_timer >= adjusted_spawn_interval:
            self.spawn_obstacle()
            self.spawn_timer = 0
    
    def spawn_obstacle(self):
        """Cria um novo obstáculo aleatório"""
        y = self.ground_y
        
        # Escolhe aleatoriamente o tipo de obstáculo
        rand = random.random()
        for prob, obs_type in self.obstacle_types:
            if rand < prob:
                if obs_type == "skeleton":
                    new_obstacle = SkeletonObstacle(pyxel.width, y, self.game_state)
                else:
                    new_obstacle = Obstacle(pyxel.width, y, self.game_state)
                break
            rand -= prob
        
        self.obstacles.append(new_obstacle)
    
    def draw(self):
        """Desenha todos os obstáculos"""
        for obstacle in self.obstacles:
            obstacle.draw()
    
    def reset(self):
        """Remove todos os obstáculos"""
        self.obstacles = []
        self.spawn_timer = 0