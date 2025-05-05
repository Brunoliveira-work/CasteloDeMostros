import pyxel
import random

class MapGenerator:
    def __init__(self, game_state):
        self.game_state = game_state
        self.tile_size = 16
        self.tileset_img = 1
        
        # Configurações do mapa infinito
        self.visible_width = 20  # Tiles visíveis horizontalmente
        self.map_height = 15     # Altura em tiles
        self.ground_level = 14   # Linha do chão
        
        # Buffer de tiles (mantém apenas o necessário)
        self.background_buffer = []
        self.ground_buffer = []
        
        # Controle de scroll
        self.scroll_x = 0.0
        self.last_tile = 0
        
        # Gera o segmento inicial
        self.generate_segment(0, self.visible_width * 2)
    
    def generate_segment(self, start_x, end_x):
        """Gera um segmento do mapa entre as posições x especificadas"""
        for x in range(start_x, end_x):
            # Background (preenche até o chão)
            for y in range(self.map_height):
                tile = random.choice([0, 1]) if y < self.ground_level else 1
                self.background_buffer.append((x, y, tile))
            
            # Chão (sempre o mesmo tile)
            self.ground_buffer.append((x, self.ground_level, 4))
    
    def update(self, dt):
        """Atualiza a posição de scroll e gerencia o buffer"""
        self.scroll_x += self.game_state.current_speed * dt * 60
        
        # Calcula o tile atual
        current_tile = int(self.scroll_x / self.tile_size)
        
        # Gera novos segmentos conforme necessário (mapa infinito)
        if current_tile > self.last_tile - self.visible_width:
            self.generate_segment(self.last_tile + 1, current_tile + self.visible_width * 2)
            self.last_tile = current_tile + self.visible_width
        
        # Remove tiles muito atrás para economizar memória
        if current_tile > 50:
            remove_threshold = current_tile - 30
            self.background_buffer = [(x, y, t) for (x, y, t) in self.background_buffer if x >= remove_threshold]
            self.ground_buffer = [(x, y, t) for (x, y, t) in self.ground_buffer if x >= remove_threshold]
    
    def draw(self, screen_width, screen_height):
        """Renderiza o mapa visível"""
        # Calcula os tiles visíveis atualmente
        start_tile = int(self.scroll_x / self.tile_size)
        end_tile = start_tile + (screen_width // self.tile_size) + 2
        
        # Desenha background
        self.draw_layer(self.background_buffer, start_tile, end_tile, screen_width, screen_height)
        
        # Desenha chão por cima
        self.draw_layer(self.ground_buffer, start_tile, end_tile, screen_width, screen_height)
    
    def draw_layer(self, layer, start_tile, end_tile, screen_width, screen_height):
        """Desenha uma camada específica do mapa"""
        for x, y, tile in layer:
            if start_tile <= x <= end_tile:
                screen_x = x * self.tile_size - self.scroll_x
                screen_y = y * self.tile_size
                
                if -self.tile_size <= screen_x <= screen_width and screen_y <= screen_height:
                    pyxel.blt(
                        int(screen_x),  # Coordenadas inteiras para evitar tremulação
                        int(screen_y),
                        self.tileset_img,
                        tile * self.tile_size, 0,
                        self.tile_size, self.tile_size,
                        pyxel.COLOR_GREEN
                    )
    
    def get_ground_y(self):
        """Retorna a posição Y do chão em pixels"""
        return self.ground_level * self.tile_size