import pyxel


class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.entities = []
    
    def add_entity(self, entity):
        self.entities.append(entity)
    
    def update(self, dt):
        for entity in self.entities:
            entity.update(dt)
    
    def draw(self, camera_x, camera_y, tile_map):
        tile_size = 16
        
        # Calcula quantos tiles precisam ser renderizados
        tiles_x = pyxel.width // tile_size + 2
        tiles_y = pyxel.height // tile_size + 2
        
        # Calcula a posição inicial no tilemap
        start_x = max(0, camera_x // tile_size)
        start_y = max(0, camera_y // tile_size)
        
        # Calcula o offset para renderização suave
        offset_x = -(camera_x % tile_size)
        offset_y = -(camera_y % tile_size)
        
        # Renderiza apenas os tiles visíveis
        for y in range(tiles_y):
            for x in range(tiles_x):
                map_x = start_x + x
                map_y = start_y + y
                
                # Verifica se está dentro dos limites do mapa
                if map_y < len(tile_map) and map_x < len(tile_map[0]):
                    tile_type = tile_map[map_y][map_x]
                    
                    # Calcula a posição na tela
                    screen_x = x * tile_size + offset_x
                    screen_y = y * tile_size + offset_y
                    
                    # Desenha o tile usando blt
                    pyxel.blt(
                        screen_x, screen_y,
                        1,  # imagem 1 contém os tiles
                        tile_type * tile_size, 0,  # u, v do tile
                        tile_size, tile_size,  # largura, altura
                        0  # cor de transparência
                    )
        
        # Depois desenha as entidades (como o jogador)
        for entity in self.entities:
            entity.draw(camera_x, camera_y)