# src/core/game/entities/player_client.py
import pyxel

class PlayerClient:
    def __init__(self, player_id: str, server):
        self.player_id = player_id
        self.server = server
        self.animation_frames = {
            "idle": [(0, 0, 16, 24)],
            "run": [(0, 0, 16, 24), (16, 0, 16, 24)],
            "jump": [(32, 0, 16, 24)],
            "duck": [(0, 24, 16, 12)]
        }
        self.current_frame = 0
        self.animation_time = 0

    def update(self, dt: float):
        # Envia inputs para o servidor
        self.server.process_input(
            self.player_id,
            pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_SPACE),
            pyxel.btn(pyxel.KEY_DOWN)
        )
        
        # Atualiza física no servidor
        self.server.update_player_physics(self.player_id, dt)
        
        # Atualiza animação
        state = self.server.get_state()["players"][self.player_id]
        self.animation_time += dt
        frames = self.animation_frames[state["last_action"]]
        
        if len(frames) > 1 and self.animation_time > 0.1:
            self.animation_time = 0
            self.current_frame = (self.current_frame + 1) % len(frames)

    def draw(self):
        state = self.server.get_state()
        player_data = state["players"][self.player_id]
        frames = self.animation_frames[player_data["last_action"]]
        u, v, w, h = frames[self.current_frame]
        
        # Ajuste para agachamento
        render_y = player_data["y"]
        if player_data["last_action"] == "duck":
            render_y += 12  # Ajuste de altura
            
        pyxel.blt(
            player_data["x"], render_y,
            0,  # Banco de imagens
            u, v, w, h,
            pyxel.COLOR_GRAY  # Cor de transparência
        )