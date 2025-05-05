import pyxel

class GameScreen:
    def __init__(self, game_client):
        self.game_client = game_client
    
    def update(self):
        """Update game state"""
        if not self.game_client.network.connected:
            return
            
        # Handle player input
        if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_SPACE):
            self.game_client.game_state_server.update_player_action(
                self.game_client.player_id, 'jump', True)
        
        if pyxel.btn(pyxel.KEY_DOWN):
            self.game_client.game_state_server.update_player_action(
                self.game_client.player_id, 'duck', True)
        else:
            self.game_client.game_state_server.update_player_action(
                self.game_client.player_id, 'duck', False)
        
        # Update game state
        self.game_client.game_state_server.update(1/60)

    def draw(self):
        """Draw game state"""
        state = self.game_client.game_state_server.get_game_state()
        
        # Provide default values if they're missing
        speed_multiplier = state.get('speed_multiplier', 1.0)
        score = state.get('score', 0)
        
        pyxel.cls(0)  # Limpa a tela
        
        # Desenha o mapa de fundo
        for x, y, tile in state['background_tiles']:
            screen_x = x * state['tile_size'] - state['scroll_x']
            screen_y = y * state['tile_size']
            
            if -state['tile_size'] <= screen_x <= state['screen_width']:
                pyxel.blt(
                    int(screen_x), int(screen_y),
                    1,  # Banco de imagens
                    tile * state['tile_size'], 0,
                    state['tile_size'], state['tile_size'],
                    pyxel.COLOR_GREEN
                )
        
        # Desenha o chão
        for x, y, tile in state['ground_tiles']:
            screen_x = x * state['tile_size'] - state['scroll_x']
            screen_y = y * state['tile_size']
            
            if -state['tile_size'] <= screen_x <= state['screen_width']:
                pyxel.blt(
                    int(screen_x), int(screen_y),
                    1,
                    tile * state['tile_size'], 0,
                    state['tile_size'], state['tile_size'],
                    pyxel.COLOR_GREEN
                )
        
        # Desenha jogadores
        for player_id, player in state['players'].items():
            color = player['color']
            is_ducking = player['is_ducking']
            
            height = player['duck_height'] if is_ducking else player['height']
            offset_y = player['height'] - height
            
            pyxel.rect(
                player['x'], player['y'] + offset_y,
                player['width'], height,
                color
            )
        
        # Desenha obstáculos
        for obstacle in state['obstacles']:
            pyxel.rect(
                obstacle['x'], obstacle['y'],
                obstacle['width'], obstacle['height'],
                pyxel.COLOR_WHITE
            )
        
        # Desenha HUD (com fallback para valores padrão)
        pyxel.text(10, 10, f"SCORE: {score}", 0)
        pyxel.text(10, 20, f"SPEED: {speed_multiplier:.1f}x", 0)
        
        if state.get('is_paused', False):
            pyxel.text(
                state.get('screen_width', 320) // 2 - 30,
                state.get('screen_height', 240) // 2,
                "GAME OVER",
                pyxel.COLOR_RED
            )