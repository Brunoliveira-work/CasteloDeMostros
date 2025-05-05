import time
import random
from typing import Dict, List, Tuple, Optional
import pyxel

class GameServer:
    def __init__(self):
        # Configurações básicas
        self.screen_width = 320
        self.screen_height = 240
        self.tile_size = 16
        self.ground_level = 14  # Linha do chão em tiles
        
        # Estado do jogo
        self.game_speed = 2.0
        self.speed_multiplier = 1.0
        self.score = 0
        self.is_paused = False
        self.start_time = time.time()
        
        # Players (armazenados como dicionário por ID)
        self.players: Dict[str, Dict] = {}
        self.last_player_id = 0
        
        # Obstáculos
        self.obstacles: List[Dict] = []
        self.spawn_timer = 0
        self.spawn_interval = 2.5
        
        # Mapa
        self.scroll_x = 0.0
        self.last_tile = 0
        self.background_buffer = []
        self.ground_buffer = []
        self._generate_initial_map()
    
    @property
    def current_speed(self) -> float:
        return self.game_speed * self.speed_multiplier
    
    def _generate_initial_map(self):
        """Gera o segmento inicial do mapa"""
        visible_width = 20
        for x in range(0, visible_width * 2):
            # Background
            for y in range(15):
                tile = random.choice([0, 1]) if y < self.ground_level else 1
                self.background_buffer.append((x, y, tile))
            
            # Chão
            self.ground_buffer.append((x, self.ground_level, 4))
    
    def add_player(self) -> str:
        """Adiciona um novo jogador e retorna seu ID"""
        player_id = str(self.last_player_id + 1)
        self.last_player_id += 1
        
        self.players[player_id] = {
            'x': 100,
            'y': (self.ground_level * self.tile_size) - 20,  # Altura padrão do player
            'width': 15,
            'height': 20,
            'duck_height': 10,
            'is_ducking': False,
            'is_jumping': False,
            'has_double_jump': True,
            'jump_velocity': 0,
            'current_frame': 0,
            'animation_time': 0,
            'color': random.randint(1, 15)  # Cor aleatória para diferenciar
        }
        
        return player_id
    
    def remove_player(self, player_id: str):
        """Remove um jogador do estado do jogo"""
        if player_id in self.players:
            del self.players[player_id]
    
    def update_player_action(self, player_id: str, action: str, value: bool):
        """Atualiza o estado de uma ação do jogador (pulo, agachar)"""
        if player_id not in self.players or self.is_paused:
            return
            
        player = self.players[player_id]
        ground_y = self.ground_level * self.tile_size
        
        if action == 'jump':
            if not player['is_jumping'] and not player['is_ducking']:
                player['is_jumping'] = True
                player['jump_velocity'] = -10 * self.speed_multiplier
            elif player['has_double_jump']:
                player['jump_velocity'] = -10 * self.speed_multiplier
                player['has_double_jump'] = False
                
        elif action == 'duck':
            if value == player['is_ducking']:
                return
                
            if not player['is_jumping']:  # Só pode agachar no chão
                if value:
                    player['y'] += (player['height'] - player['duck_height'])
                else:
                    player['y'] -= (player['height'] - player['duck_height'])
            
            player['is_ducking'] = value
    
    def update(self, dt: float):
        """Atualiza o estado do jogo (chamado em loop)"""
        if self.is_paused:
            return
            
        # Ajusta o dt para evitar saltos grandes
        dt = min(dt, 0.033)
        adjusted_dt = dt * self.speed_multiplier
        
        # Atualiza velocidade e pontuação
        current_time = time.time()
        if current_time - self.start_time > 10:
            self.speed_multiplier += 0.05
            self.start_time = current_time
        
        self.score += 2 * adjusted_dt
        
        # Atualiza scroll do mapa
        self.scroll_x += self.current_speed * dt * 60
        current_tile = int(self.scroll_x / self.tile_size)
        
        # Gera novos segmentos do mapa conforme necessário
        if current_tile > self.last_tile - 20:
            for x in range(self.last_tile + 1, current_tile + 40):
                for y in range(15):
                    tile = random.choice([0, 1]) if y < self.ground_level else 1
                    self.background_buffer.append((x, y, tile))
                self.ground_buffer.append((x, self.ground_level, 4))
            self.last_tile = current_tile + 20
        
        # Remove tiles muito atrás
        if current_tile > 50:
            remove_threshold = current_tile - 30
            self.background_buffer = [(x, y, t) for (x, y, t) in self.background_buffer if x >= remove_threshold]
            self.ground_buffer = [(x, y, t) for (x, y, t) in self.ground_buffer if x >= remove_threshold]
        
        # Atualiza jogadores
        ground_y = self.ground_level * self.tile_size
        for player in self.players.values():
            if player['is_jumping']:
                player['y'] += player['jump_velocity'] * dt * 60
                player['jump_velocity'] += 0.6 * self.speed_multiplier * dt * 60
                
                if player['y'] + (player['duck_height'] if player['is_ducking'] else player['height']) >= ground_y:
                    player['y'] = ground_y - (player['duck_height'] if player['is_ducking'] else player['height'])
                    player['is_jumping'] = False
                    player['jump_velocity'] = 0
                    player['has_double_jump'] = True
            
            # Atualiza animação
            player['animation_time'] += dt
            if player['animation_time'] >= (0.1 / self.speed_multiplier):
                player['animation_time'] = 0
                player['current_frame'] = (player['current_frame'] + 1) % 4  # 4 frames de animação
        
        # Atualiza obstáculos
        self._update_obstacles(adjusted_dt)
        
        # Verifica colisões
        self._check_collisions()
    
    def _update_obstacles(self, dt: float):
        """Atualiza obstáculos existentes e gera novos"""
        # Remove obstáculos fora da tela
        self.obstacles = [obs for obs in self.obstacles if obs['x'] + obs['width'] > -50]
        
        # Atualiza posição dos obstáculos
        for obstacle in self.obstacles:
            obstacle['x'] -= self.current_speed * dt * 60
            obstacle['animation_time'] += dt
            if obstacle['animation_time'] >= 0.2:
                obstacle['animation_time'] = 0
                obstacle['current_frame'] = (obstacle['current_frame'] + 1) % 2
        
        # Gera novos obstáculos
        self.spawn_timer += dt
        if self.spawn_timer >= (self.spawn_interval / (self.speed_multiplier ** 0.8)):
            self.spawn_timer = 0
            if random.random() < 0.3:  # 30% de chance de spawn
                self.obstacles.append({
                    'x': self.screen_width,
                    'y': (self.ground_level * self.tile_size) - 24,
                    'width': 10,
                    'height': 24,
                    'type': 'skeleton',
                    'current_frame': 0,
                    'animation_time': 0
                })
    
    def _check_collisions(self):
        """Verifica colisões entre jogadores e obstáculos"""
        for player_id, player in self.players.items():
            player_rect = (
                player['x'],
                player['y'] + (player['height'] - (player['duck_height'] if player['is_ducking'] else player['height'])),
                player['width'],
                player['duck_height'] if player['is_ducking'] else player['height']
            )
            
            for obstacle in self.obstacles:
                obstacle_rect = (
                    obstacle['x'],
                    obstacle['y'],
                    obstacle['width'],
                    obstacle['height']
                )
                
                if self._check_rect_collision(player_rect, obstacle_rect):
                    self.is_paused = True
                    return
    
    def _check_rect_collision(self, rect1: Tuple, rect2: Tuple) -> bool:
        """Verifica colisão entre dois retângulos (x, y, w, h)"""
        return (rect1[0] < rect2[0] + rect2[2] and
                rect1[0] + rect1[2] > rect2[0] and
                rect1[1] < rect2[1] + rect2[3] and
                rect1[1] + rect1[3] > rect2[1])
    
    def get_game_state(self) -> Dict:
        """Retorna o estado atual do jogo para renderização"""
        return {
            'screen_width': self.screen_width,
            'screen_height': self.screen_height,
            'scroll_x': self.scroll_x,
            'score': int(self.score),
            'speed_multiplier': self.speed_multiplier,
            'is_paused': self.is_paused,
            'players': self.players,
            'obstacles': self.obstacles,
            'background_tiles': self.background_buffer,
            'ground_tiles': self.ground_buffer,
            'tile_size': self.tile_size,
            'ground_level': self.ground_level
        }