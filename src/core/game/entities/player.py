import pyxel

class Player:
    def __init__(self, x, ground_y, game_state):
        self.game_state = game_state
        self.width = 15
        self.height = 20
        self.duck_height = 10
        self.x = x
        self.y = ground_y - self.height
        
        # Estados
        self.is_ducking = False
        self.is_jumping = False
        self.has_double_jump = True
        
        # Física (valores base, serão afetados pela velocidade)
        self.base_gravity = 0.6
        self.base_jump_strength = -10
        self.base_double_jump_strength = -10
        
        # Animação
        self.animation_frames = []
        self.current_frame = 0
        self.animation_time = 0
        self.base_animation_speed = 0.1
        
        self._load_animations()
    
    def _load_animations(self):
        """Carrega as animações do arquivo"""
        with open("../assets/animations/player/knight_sprite.shape", "r") as f:
            for line in f:
                if line.startswith("move"):
                    parts = line.split()
                    x = int(parts[1])
                    y = int(parts[2])
                    w = int(parts[3])
                    h = int(parts[4])
                    self.animation_frames.append((x, y, w, h))
    
    @property
    def gravity(self):
        return self.base_gravity * self.game_state.speed_multiplier
    
    @property
    def jump_strength(self):
        return self.base_jump_strength * self.game_state.speed_multiplier
    
    @property
    def double_jump_strength(self):
        return self.base_double_jump_strength * self.game_state.speed_multiplier
    
    @property
    def animation_speed(self):
        return self.base_animation_speed / self.game_state.speed_multiplier
    
    def update(self, ground_y, dt):
        """Atualiza com delta time ajustado"""
        # Controles (não são afetados pela velocidade)
        if (pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_SPACE)):
            self.jump()
        
        if pyxel.btn(pyxel.KEY_DOWN):
            self.duck(True)
        else:
            self.duck(False)
        
        # Física (afetada pela velocidade)
        if self.is_jumping:
            self.y += self.jump_velocity * dt * 60  # Ajuste para manter velocidade
            self.jump_velocity += self.gravity * dt * 60
            
            if self.y + (self.duck_height if self.is_ducking else self.height) >= ground_y:
                self.y = ground_y - (self.duck_height if self.is_ducking else self.height)
                self.is_jumping = False
                self.jump_velocity = 0
                self.has_double_jump = True
        
        # Animação (mais rápida conforme velocidade aumenta)
        self.animation_time += dt
        if self.animation_time >= self.animation_speed:
            self.animation_time = 0
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
    
    def jump(self):
        """Controla o pulo e double jump"""
        if not self.is_jumping and not self.is_ducking:
            # Primeiro pulo
            self.is_jumping = True
            self.jump_velocity = self.jump_strength
        elif self.has_double_jump:
            # Segundo pulo (double jump)
            self.jump_velocity = self.double_jump_strength
            self.has_double_jump = False
    
    def duck(self, is_ducking):
        """Controla o estado de agachado"""
        if is_ducking == self.is_ducking:
            return
            
        if not self.is_jumping:  # Só pode agachar no chão
            if is_ducking:
                self.y += (self.height - self.duck_height)
            else:
                self.y -= (self.height - self.duck_height)
        
        self.is_ducking = is_ducking
    
    def draw(self):
        """Desenha o player com a animação atual"""
        if self.is_ducking:
            frame = (0, 0, self.width, self.duck_height)
        else:
            frame = self.animation_frames[self.current_frame]
        
        pyxel.blt(
            self.x, 
            self.y + (self.height - frame[3]),
            0,
            frame[0], frame[1],
            frame[2], frame[3],
            pyxel.COLOR_GRAY
        )
    
    def is_alive(self):
        return True
    
    def get_hitbox(self):
        """Retorna a hitbox do player como (x, y, width, height)"""
        if self.is_ducking:
            return (self.x, self.y + (self.height - self.duck_height), 
                    self.width, self.duck_height)
        return (self.x, self.y, self.width, self.height)
    
    def check_collision(self, obstacle):
        """Verifica colisão com um obstáculo"""
        player_x, player_y, player_w, player_h = self.get_hitbox()
        obstacle_x, obstacle_y, obstacle_w, obstacle_h = (
            obstacle.x, obstacle.y, obstacle.width, obstacle.height
        )
        
        # Verifica se os retângulos se sobrepõem
        return (player_x < obstacle_x + obstacle_w and
                player_x + player_w > obstacle_x and
                player_y < obstacle_y + obstacle_h and
                player_y + player_h > obstacle_y)
        

class PlayerRenderer:
    def __init__(self, image_bank: int = 0):
        self.image_bank = image_bank
    
    def draw(self, player_data: dict):
        try:
            anim_state = player_data['animation_state']
            anim = player_data['sprite_data'][anim_state]
            frame_idx = int(player_data['anim_progress'] / anim.speed) % len(anim.frames) if anim.speed > 0 else 0
            u, v, w, h = anim.frames[frame_idx]
            
            render_y = player_data['y']
            if anim_state == 'duck':
                render_y += player_data['height'] - h
            
            pyxel.blt(
                player_data['x'], render_y,
                self.image_bank,
                u, v, w, h,
                pyxel.COLOR_GRAY
            )
        except KeyError as e:
            print(f"Erro ao renderizar jogador: {e}. Dados recebidos: {player_data}")