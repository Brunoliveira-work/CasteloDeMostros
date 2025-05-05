import pyxel
import socket
import json
import time
import random
import multiprocessing
from typing import Dict, List, Tuple, Optional
from enum import Enum, auto
import sys

# Constantes
PORT = 5600
BUFFER_SIZE = 4096

class GameState(Enum):
    LOBBY = auto()
    PLAYING = auto()
    GAME_OVER = auto()

class GameServer(multiprocessing.Process):
    def __init__(self):
        super().__init__()
        self.players = {}
        self.game_state = GameState.LOBBY
        self.lock = multiprocessing.Lock()
        
        # Configurações do jogo
        self.screen_width = 320
        self.screen_height = 240
        self.tile_size = 16
        self.ground_level = 14
        
        # Estado do jogo
        self.game_speed = 2.0
        self.speed_multiplier = 1.0
        self.score = 0
        self.start_time = time.time()
        
        # Seed compartilhada para geração do mapa
        self.map_seed = random.randint(0, 999999)
        
        # Frames de animação aleatorios
        self.animation_frames = [
            (0, 0, 16, 16),   # Frame 0 
            (16, 0, 16, 16),   # Frame 1 
            (32, 0, 16, 16),   # Frame 2 
            (48, 0, 16, 16)    # Frame 3 
        ]
        
        # Obstáculos
        self.scroll_x = 0.0
        self.obstacles = []
        self.spawn_timer = 0
        self.spawn_interval = 2.5
        
        self.obstacle_types = {
            'skeleton': {
                'width': 10,
                'height': 12,
                'animation_frames': [
                    (0, 96, 10, 12),  # Frame 1
                    (17, 94, 10, 14)   # Frame 2
                ],
                'animation_speed': 0.2
            },
            'diabrete': {
                'width': 65,
                'height': 12,
                'animation_frames': [
                    (0, 114, 10, 11),  # Frame 1
                    (17, 113, 10, 12)   # Frame 2
                ],
                'animation_speed': 0.2
            }
        }
    
    def add_player(self, player_id: str):
        """Adiciona um novo jogador com todas as chaves necessárias"""
        with self.lock:
            if len(self.players) >= 2:
                raise Exception("O jogo já atingiu o número máximo de jogadores (2)")
            char_type = 'knight' if len(self.players) == 0 else 'mage'
        
            self.players[player_id] = {
                'x': 100 - 50*(int(player_id) -1),
                'y': (self.ground_level * self.tile_size) - 20,
                'width': 15,
                'height': 20,
                'duck_height': 10,
                'is_ducking': False,
                'is_jumping': False,
                'has_double_jump': True,
                'jump_velocity': 0,
                'current_frame': 0,
                'animation_time': 0,
                'color': pyxel.COLOR_GRAY,
                'ready': False,
                'sprite_frame': 0,
                'sprite_x': 0,
                'sprite_y': 0,
                'sprite_w': 16,
                'sprite_h': 16,
                'char_type': char_type  # Adiciona o tipo de personagem
            }
    
    def update_player_action(self, player_id: str, action: str, value: bool):
        """Atualiza o estado de uma ação do jogador"""
        with self.lock:
            if player_id not in self.players or self.game_state != GameState.PLAYING:
                return
                
            player = self.players[player_id]
            ground_y = self.ground_level * self.tile_size
            
            # Garante que as chaves essenciais existam
            if 'is_ducking' not in player:
                player['is_ducking'] = False
            if 'is_jumping' not in player:
                player['is_jumping'] = False
            if 'has_double_jump' not in player:
                player['has_double_jump'] = True
            

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
                    
                if not player['is_jumping']:
                    if value:
                        player['y'] += (player['height'] - player['duck_height'])
                    else:
                        player['y'] -= (player['height'] - player['duck_height'])
                
                player['is_ducking'] = value
    
    def update_game_state(self, dt: float):
        """Atualiza o estado do jogo"""
        if self.game_state != GameState.PLAYING:
            return
            
        with self.lock:
            # Ajusta o dt para evitar saltos grandes
            dt = min(dt, 0.033)
            adjusted_dt = dt * self.speed_multiplier
            
            # Atualiza velocidade e pontuação
            current_time = time.time()
            if current_time - self.start_time > 10:
                self.speed_multiplier += 0.05
                self.start_time = current_time
            
            self.score += 2 * adjusted_dt
            
            # Atualiza scroll do jogo
            self.scroll_x += self.game_speed * self.speed_multiplier * dt * 60
            
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
                    player['current_frame'] = (player['current_frame'] + 1) % len(self.animation_frames)
                    
                    # Atualiza o frame do sprite
                    frame = player['current_frame']
                    player['sprite_x'], player['sprite_y'], player['sprite_w'], player['sprite_h'] = self.animation_frames[frame]
            
            # Atualiza obstáculos
            self._update_obstacles(adjusted_dt)
            
            # Verifica colisões
            if self._check_collisions():
                self.game_state = GameState.GAME_OVER
    
    def _update_obstacles(self, dt: float):
        """Atualiza obstáculos existentes e gera novos"""
        # Remove obstáculos fora da tela
        self.obstacles = [obs for obs in self.obstacles if obs['x'] + obs['width'] > -50]
        
        # Atualiza posição e animação dos obstáculos
        for obstacle in self.obstacles:
            obstacle['x'] -= self.game_speed * self.speed_multiplier * dt * 60
            
            obstacle['animation_time'] += dt
            if (obstacle['animation_time'] >= self.obstacle_types[obstacle['type']]['animation_speed']):
                obstacle['animation_time'] = 0
                obstacle['current_frame'] = (obstacle['current_frame'] + 1) % len(self.obstacle_types[obstacle['type']]['animation_frames'])
        
        # Gera novos obstáculos
        self.spawn_timer += dt
        if self.spawn_timer >= (self.spawn_interval / (self.speed_multiplier ** 0.8)):
            self.spawn_timer = 0
            if random.random():
                obstacle_type = 'skeleton' if random.random() > 0.3 else 'diabrete'
                if obstacle_type == 'skeleton':
                    self.obstacles.append({
                        'x': self.screen_width,
                        'y': (self.ground_level * self.tile_size) - self.obstacle_types['skeleton']['height'],
                        'width': self.obstacle_types['skeleton']['width'],
                        'height': self.obstacle_types['skeleton']['height'],
                        'type': 'skeleton',
                        'current_frame': 0,
                        'animation_time': 0,
                        'animation_frames': self.obstacle_types['skeleton']['animation_frames']
                    })
                else:
                    self.obstacles.append({
                        'x': self.screen_width,
                        'y': (self.ground_level * self.tile_size) - self.obstacle_types['diabrete']['height'],
                        'width': self.obstacle_types['diabrete']['width'],
                        'height': self.obstacle_types['diabrete']['height'],
                        'type': 'diabrete',
                        'current_frame': 0,
                        'animation_time': 0,
                        'animation_frames': [self.obstacle_types['diabrete']['animation_frames']]
                    })
    
    def _check_collisions(self) -> bool:
        """Verifica colisões entre jogadores e obstáculos"""
        for player in self.players.values():
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
                    return True
        return False
    
    def _check_rect_collision(self, rect1: Tuple, rect2: Tuple) -> bool:
        """Verifica colisão entre dois retângulos"""
        return (rect1[0] < rect2[0] + rect2[2] and
                rect1[0] + rect1[2] > rect2[0] and
                rect1[1] < rect2[1] + rect2[3] and
                rect1[1] + rect1[3] > rect2[1])
    
    def start_game(self):
        """Inicia o jogo"""
        with self.lock:
            if self.game_state == GameState.LOBBY and len(self.players) > 0:
                self.game_state = GameState.PLAYING
                self.start_time = time.time()
    
    def set_player_ready(self, player_id: str, ready: bool):
        """Define se um jogador está pronto"""
        with self.lock:
            if player_id in self.players:
                self.players[player_id]['ready'] = ready
    
    
    def get_lobby_state(self) -> Dict:
        """Retorna o estado do lobby garantindo todas as chaves"""
        with self.lock:
            players_data = {}
            for player_id, player in self.players.items():
                players_data[player_id] = {
                    'color': player.get('color', random.randint(1, 15)),
                    'ready': player.get('ready', False),
                    'name': f"Player {player_id}"  # Nome padrão
                }

            return {
                'players': players_data,
                'game_state': self.game_state.name,
                'map_seed': self.map_seed,
                'server_time': time.time(),
                'player_count': len(self.players)
            }
    
    def get_game_state(self) -> Dict:
        """Retorna o estado completo do jogo garantindo todas as chaves necessárias"""
        with self.lock:
            # Garante que todos os jogadores tenham a estrutura mínima necessária
            players_data = {}
            for player_id, player in self.players.items():
                players_data[player_id] = {
                    'x': player.get('x', 100),
                    'y': player.get('y', (self.ground_level * self.tile_size) - 20),
                    'width': player.get('width', 15),
                    'height': player.get('height', 20),
                    'duck_height': player.get('duck_height', 10),
                    'is_ducking': player.get('is_ducking', False),
                    'is_jumping': player.get('is_jumping', False),
                    'color': player.get('color', random.randint(1, 15)),
                    'current_frame': player.get('current_frame', 0),
                    'sprite_x': player.get('sprite_x', 0),
                    'sprite_y': player.get('sprite_y', 0),
                    'sprite_w': player.get('sprite_w', 16),
                    'sprite_h': player.get('sprite_h', 16)
                }

            return {
                'players': players_data,
                'scroll_x': self.scroll_x,
                'score': int(self.score),
                'speed_multiplier': self.speed_multiplier,
                'game_state': self.game_state.name,
                'tile_size': self.tile_size,
                'ground_level': self.ground_level,
                'screen_width': self.screen_width,
                'screen_height': self.screen_height,
                'timestamp': time.time(),  # Para debug
                'obstacles': self.obstacles,
            }
        
    def run(self):
        """Executa o servidor com tratamento de porta em uso"""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            # Configura opção para reutilizar porta
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Tenta vincular à porta, se falhar tenta portas próximas
            port = PORT
            max_attempts = 5
            for attempt in range(max_attempts):
                try:
                    sock.bind(('0.0.0.0', port))
                    print(f"Servidor iniciado na porta {port}")
                    break
                except OSError as e:
                    if "Address already in use" in str(e) and attempt < max_attempts - 1:
                        port += 1
                        print(f"Porta {port-1} em uso, tentando {port}...")
                        continue
                    raise e
            
            last_update = time.time()
            
            while True:
                try:
                    data, addr = sock.recvfrom(BUFFER_SIZE)
                    request = json.loads(data.decode())
                    
                    response = {'status': 'ok', 'data': None}  # Estrutura base
                    command = request.get('command')
                    
                    if request.get('command') == 'get_lobby':
                        response['data'] = self.get_lobby_state()
                        
                    
                    if command == 'join':
                        player_id = str(len(self.players) + 1)
                        self.add_player(player_id)
                        response = {'status': 'ok', 'player_id': player_id}
                    
                    elif command == 'get_lobby':
                        response = {'status': 'ok', 'data': self.get_lobby_state()}
                    
                    elif command == 'get_game':
                        response = {'status': 'ok', 'data': self.get_game_state()}
                    
                    elif command == 'player_action':
                        player_id = request['player_id']
                        action = request['action']
                        value = request['value']
                        self.update_player_action(player_id, action, value)
                        response = {'status': 'ok'}
                    
                    elif command == 'set_ready':
                        player_id = request['player_id']
                        ready = request['ready']
                        self.set_player_ready(player_id, ready)
                        response = {'status': 'ok'}
                    
                    elif command == 'start_game':
                        self.start_game()
                        response = {'status': 'ok'}
                    
                    else:
                        response = {'status': 'error', 'message': 'Comando inválido'}
                    
                    sock.sendto(json.dumps(response).encode(), addr)
                    
                    # Atualiza o jogo a 60 FPS
                    current_time = time.time()
                    if current_time - last_update >= 1/60:
                        self.update_game_state(current_time - last_update)
                        last_update = current_time
                
                except Exception as e:
                    print(f"Erro no servidor: {e}")

class GameClient:
    def __init__(self, is_host=False, server_ip='localhost'):
        self.is_host = is_host
        self.server_ip = server_ip
        self.player_id = None
        self.game_state = GameState.LOBBY
        self.local_state = {}
        self.map_seed = None
        self.tile_size = 16
        self.screen_width = 320
        self.ground_level = 14
        self.local_map = {'background_tiles': [], 'ground_tiles': []}
        
        # Configurações do mapa
        self.map_width = 100  # Número de tiles horizontais no mapa
        self.background_buffer = []  # Lista de tuplas (x, y, tile)
        self.ground_buffer = []      # Lista de tuplas (x, y, tile)
        self.last_tile = 0           # Último tile gerado 

        
        # Shared state between processes
        self.shared_state = multiprocessing.Manager().dict()
        self.shared_state['running'] = True
        self.shared_state['game_state'] = GameState.LOBBY.name
        self.shared_state['local_state'] = {}
        self.shared_state['map_seed'] = None

        # Event for signaling updates
        self.update_event = multiprocessing.Event()

        # Inicializa a janela
        pyxel.init(320, 240, title="Castelo de Monstros", fps=60)
        
        pyxel.load("./my_music.pyxres")
        
        # Carrega assets
        pyxel.image(0).load(0, 0, "./assets/animations/player/banco_0.png")
        pyxel.image(1).load(0, 0, "./assets/animations/player/castle-tileset.png")

        
        self.animation_frames = self._load_animations('knight')
        self.mage_animation_frames = self._load_animations('mage')
        
        self._generate_initial_map()
        
        self.obstacle_sprites = {
            'skeleton': [
                (0, 96, 10, 12),  # Frame 1
                (17, 94, 10, 14)    # Frame 2
            ],
            'diabrete': [
                    (0, 114, 10, 11),  # Frame 1
                    (17, 113, 10, 12)   # Frame 2
                ]
        }
        
        # Se for host, inicia o servidor em um processo separado
        if self.is_host:
            self.server_process = GameServer()
            self.server_process.start()
            time.sleep(1)  # Espera o servidor iniciar
        
        # Conecta ao servidor
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._join_server()
        
        # Processo para receber atualizações do servidor
        self.update_process = multiprocessing.Process(
            target=self._update_loop, 
            daemon=True
        )
        self.update_process.start()
        
        # Inicia o loop do jogo
        pyxel.run(self.update, self.draw)
    
    def _load_animations(self, string: str) -> List[Tuple[int, int, int, int]]:
        """Carrega as animações do arquivo"""
        tmp = []
        with open(f"./assets/animations/player/{string}_sprite.shape", "r") as f:
            
            for line in f:
                if line.startswith("move"):
                    parts = line.split()
                    x = int(parts[1])
                    y = int(parts[2])
                    w = int(parts[3])
                    h = int(parts[4])
                    tmp.append((x, y, w, h))
        return tmp

    def _generate_initial_map(self):
        """Gera o segmento inicial do mapa"""
        visible_width = 20
        for x in range(0, visible_width * 2):
            # Background
            for y in range(self.ground_level + 1):  # +1 para incluir o ground_level
                tile = random.choice([0, 1]) if y < self.ground_level else 1
                self.background_buffer.append((x, y, tile))
            
            # Chão
            self.ground_buffer.append((x, self.ground_level, 4))
        
        self.last_tile = visible_width * 2 - 1

    def _update_map(self, scroll_x: float):
        """Atualiza o mapa conforme o scroll avança"""
        if not self.local_state:
            return
            
        tile_size = self.local_state.get('tile_size', 16)
        current_tile = int(scroll_x / tile_size)
        
        # Gera novos segmentos do mapa conforme necessário
        if current_tile > self.last_tile - 20:
            for x in range(self.last_tile + 1, current_tile + 40):
                # Background
                for y in range(self.ground_level + 1):
                    tile = random.choice([0, 1]) if y < self.ground_level else 1
                    self.background_buffer.append((x, y, tile))
                
                # Chão
                self.ground_buffer.append((x, self.ground_level, 4))
            
            self.last_tile = current_tile + 20
        
        # Remove tiles muito atrás (otimização de memória)
        if current_tile > 50:
            remove_threshold = current_tile - 30
            self.background_buffer = [
                (x, y, t) for (x, y, t) in self.background_buffer 
                if x >= remove_threshold
            ]
            self.ground_buffer = [
                (x, y, t) for (x, y, t) in self.ground_buffer 
                if x >= remove_threshold
            ]

    def _draw_map(self):
        """Desenha o mapa na tela"""
        if not self.local_state:
            return
            
        state = self.local_state
        tile_size = state.get('tile_size', 16)
        scroll_x = state.get('scroll_x', 0)
        screen_width = state.get('screen_width', 320)
        
        # Desenha o background
        for x, y, tile in self.background_buffer:
            screen_x = x * tile_size - scroll_x
            screen_y = y * tile_size
            
            # Só desenha se estiver visível ou parcialmente visível
            if -tile_size <= screen_x <= screen_width:
                pyxel.blt(
                    int(screen_x), int(screen_y),
                    1,  # Banco de imagens
                    tile * tile_size, 0,
                    tile_size, tile_size,
                    pyxel.COLOR_GREEN
                )
        
        # Desenha o chão
        for x, y, tile in self.ground_buffer:
            screen_x = x * tile_size - scroll_x
            screen_y = y * tile_size
            
            if -tile_size <= screen_x <= screen_width:
                pyxel.blt(
                    int(screen_x), int(screen_y),
                    1,
                    tile * tile_size, 0,
                    tile_size, tile_size,
                    pyxel.COLOR_GREEN
                )
        
    def _join_server(self):
        """Registra o jogador no servidor com tratamento de falhas"""
        max_attempts = 3
        for attempt in range(max_attempts):
            response = self._send_request({'command': 'join'})
            
            if response and response.get('status') == 'ok':
                self.player_id = response['player_id']
                print(f"Conectado como jogador {self.player_id}")
                return True
            elif response and response.get('message') == 'O jogo já atingiu o número máximo de jogadores (2)':
                print("O jogo já está cheio (2 jogadores)")
                pyxel.quit()
                sys.exit(1)
            else:
                error_msg = response.get('message', 'Erro desconhecido') if response else 'Sem resposta'
                print(f"Tentativa {attempt + 1} de {max_attempts} falhou: {error_msg}")
                if attempt < max_attempts - 1:
                    time.sleep(1)
        
        print("Não foi possível conectar ao servidor")
        return False
        

    def _send_request(self, request: Dict) -> Optional[Dict]:
        """Envia requisição com tratamento de timeout e reconexão"""
        try:
            if not isinstance(request, dict):
                return {'status': 'error', 'message': 'Requisição inválida'}
                
            request['timestamp'] = time.time()
            if hasattr(self, 'player_id') and self.player_id:
                request['player_id'] = self.player_id
                
            # Tenta enviar para a porta padrão e portas próximas
            max_port_attempts = 3
            for port_offset in range(max_port_attempts):
                current_port = PORT + port_offset
                try:
                    self.sock.sendto(json.dumps(request).encode(), (self.server_ip, current_port))
                    self.sock.settimeout(2.0)
                    data, _ = self.sock.recvfrom(BUFFER_SIZE)
                    return json.loads(data.decode())
                except socket.timeout:
                    if port_offset == max_port_attempts - 1:
                        return {'status': 'error', 'message': 'Timeout - servidor não respondeu'}
                    continue
                except ConnectionResetError:
                    if port_offset == max_port_attempts - 1:
                        return {'status': 'error', 'message': 'Conexão redefinida pelo servidor'}
                    continue
                    
        except Exception as e:
            return {'status': 'error', 'message': f"Erro de comunicação: {str(e)}"}

    def _validate_response(self, response: Dict, required_keys: List[str]) -> bool:
        """Valida se a resposta contém todas as chaves necessárias"""
        if not isinstance(response, dict):
            # print("Resposta não é um dicionário")
            return False
        
        if response.get('status') != 'ok':
            print(f"Erro no servidor: {response.get('message', 'Sem mensagem')}")
            return False
        
        if 'data' not in response:
            # print("Resposta sem campo 'data'")
            return False
        
        missing_keys = [key for key in required_keys if key not in response['data']]
        if missing_keys:
            # print(f"Dados incompletos. Faltando: {missing_keys}")
            return False
        
        return True

    def _update_loop(self):
        """Loop de atualização com multiprocessing"""
        while self.shared_state['running']:
            try:
                lobby_response = self._send_request({'command': 'get_lobby'})
                if self._validate_response(lobby_response, ['players', 'game_state', 'map_seed']):
                    self.shared_state['game_state'] = lobby_response['data']['game_state']
                    new_seed = lobby_response['data']['map_seed']
                    if new_seed != self.shared_state.get('map_seed'):
                        self.shared_state['map_seed'] = new_seed

                if GameState[self.shared_state['game_state']] == GameState.PLAYING:
                    game_response = self._send_request({'command': 'get_game'})
                    if self._validate_response(game_response, ['players', 'scroll_x', 'score', 'tile_size', 'ground_level']):
                        self.shared_state['local_state'] = game_response['data']

                
            except Exception as e:
                print(f"Erro no loop: {str(e)}")
                time.sleep(1)

    def update(self):
        """Atualiza o estado do cliente e envia inputs para o servidor"""
        # Sync with shared state
        self.game_state = GameState[self.shared_state['game_state']]
        self.local_state = self.shared_state['local_state']
        self.map_seed = self.shared_state['map_seed']
        
        if self.game_state == GameState.PLAYING:
            scroll_x = self.local_state.get('scroll_x', 0)
            self._update_map(scroll_x)

        if self.game_state == GameState.LOBBY:
            if pyxel.btnp(pyxel.KEY_RETURN) and self.is_host:
                self._send_request({'command': 'start_game'})
            
            if pyxel.btnp(pyxel.KEY_R):
                self._send_request({
                    'command': 'set_ready',
                    'player_id': self.player_id,
                    'ready': True
                })
        
        elif self.game_state == GameState.PLAYING:
            # Envia ações do jogador para o servidor
            if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_SPACE):
                self._send_request({
                    'command': 'player_action',
                    'player_id': self.player_id,
                    'action': 'jump',
                    'value': True
                })
                pyxel.play(0, 0)  # Toca som de pulo
            
            # if pyxel.btn(pyxel.KEY_DOWN):
            #     self._send_request({
            #         'command': 'player_action',
            #         'player_id': self.player_id,
            #         'action': 'duck',
            #         'value': True
            #     })
                
            # else:
            #     self._send_request({
            #         'command': 'player_action',
            #         'player_id': self.player_id,
            #         'action': 'duck',
            #         'value': False
            #     })

    def draw(self):
        """Renderiza o jogo baseado no estado local"""
        pyxel.cls(7)  # Limpa a tela
        
        if self.game_state == GameState.LOBBY:
            self._draw_lobby()
        elif self.game_state == GameState.PLAYING:
            self._draw_game()
        elif self.game_state == GameState.GAME_OVER:
            self._draw_game_over()

    def _draw_lobby(self):
        """Desenha a tela de lobby"""
        pyxel.text(100, 50, "LOBBY MULTIPLAYER", 0)
        pyxel.text(100, 70, f"Seu ID: {self.player_id}", 0)
        
        response = self._send_request({'command': 'get_lobby'})
        
        # Verifica se a resposta é válida antes de acessar 'data'
        if not response or response.get('status') != 'ok' or 'data' not in response:
            pyxel.text(100, 100, "Aguardando conexão com servidor...", 8)
            return
            
        lobby_state = response['data']
        
        y = 100
        for player_id, player in lobby_state['players'].items():
            color = player['color']
            status = "PRONTO" if player['ready'] else "AGUARDANDO"
            prefix = "> " if player_id == self.player_id else "  "
            pyxel.text(100, y, f"{prefix}Jogador {player_id} ({status})", color)
            y += 15
        
        if self.is_host:
            pyxel.text(100, 180, "Pressione ENTER para iniciar o jogo", 0)
        
        pyxel.text(100, 200, "Pressione R para marcar como pronto", 0)

    def _draw_game(self):
        """Desenha o jogo em si"""
        if not self.local_state:
            return
        
        pyxel.cls(0)  # Limpa a tela
        
        
        self._draw_map()
        
        # Desenha jogadores
        for player_id, player in self.local_state.get('players', {}).items():
            if not all(key in player for key in ['x', 'y', 'width', 'height', 'color']):
                continue
            
            # Obtém o frame de animação atual
            # Obtém o tipo de personagem
            char_type = 'knight' if int(player_id) == 1 else 'mage'
            
            # print(f"Player {player_id}")
            
            # Define os sprites baseados no tipo de personagem
            if char_type == 'knight':
                # Frames de animação do cavaleiro
                frame = player.get('current_frame', 0) % len(self.animation_frames)
                sprite_x, sprite_y, sprite_w, sprite_h = self.animation_frames[frame]
            else:  # mage
                # Frames de animação do mago (você precisará definir esses valores)
                # Exemplo - você precisará ajustar conforme seus sprites
                frame = player.get('current_frame', 0) % len(self.mage_animation_frames)
                sprite_x, sprite_y, sprite_w, sprite_h = self.mage_animation_frames[frame]
                
            color = player.get('color', pyxel.COLOR_GRAY)
            
            # Desenha o sprite do jogador
            pyxel.blt(
                player['x'], player['y'] + (player['height'] - sprite_h),  # Ajusta a posição Y
                0,  # Banco de imagens 0 (onde está o sprite do jogador)
                sprite_x, sprite_y,
                sprite_w, sprite_h,
                color
            )
        
        # Desenha obstáculos
        for obstacle in self.local_state.get('obstacles', []):
            if obstacle['type'] == 'skeleton':
                frame = self.obstacle_sprites['skeleton'][obstacle.get('current_frame', 0)]
                pyxel.blt(
                    obstacle['x'],
                    obstacle['y'] + (obstacle['height'] - frame[3]),  # Ajusta a posição Y
                    0,  # Banco de imagens
                    frame[0], frame[1],  # u, v
                    frame[2], frame[3],  # w, h
                    pyxel.COLOR_GREEN  # Cor de transparência
                )
            elif obstacle['type'] == 'diabrete':
                frame = self.obstacle_sprites['diabrete'][obstacle.get('current_frame', 0)]
                for i in range(5):
                    pyxel.blt(
                        obstacle['x'] + i * (frame[2]+2),  # Desloca o sprite para a direita
                        obstacle['y'] + (obstacle['height'] - frame[3]),
                        0,
                        frame[0], frame[1],
                        frame[2], frame[3],
                        pyxel.COLOR_GREEN
                    )
        
        # Desenha HUD
        pyxel.text(10, 10, f"SCORE: {self.local_state.get('score', 0)}", 7)
        pyxel.text(10, 20, f"SPEED: {self.local_state.get('speed_multiplier', 1.0):.1f}x", 7)

    def _draw_game_over(self):
        """Desenha a tela de game over"""
        screen_width = self.local_state.get('screen_width', 320)
        screen_height = self.local_state.get('screen_height', 240)
        
        # Toca som de morte apenas uma vez
        if not hasattr(self, 'death_sound_played'):
            pyxel.play(1, 1)
            self.death_sound_played = True
        
        pyxel.text(
            screen_width // 2 - 30,
            screen_height // 2,
            "GAME OVER",
            pyxel.COLOR_RED
        )
        
        pyxel.text(
            screen_width // 2 - 40,
            screen_height // 2 + 20,
            f"SCORE FINAL: {self.local_state.get('score', 0)}",
            pyxel.COLOR_BLACK
        )
        
        if self.game_state != GameState.GAME_OVER:
            self.death_sound_played = False

    def __del__(self):
        """Cleanup when the client is destroyed"""
        self.shared_state['running'] = False
        if hasattr(self, 'update_process'):
            self.update_process.terminate()
        if hasattr(self, 'server_process') and self.is_host:
            self.server_process.terminate()

def main():
    import sys
    
    if len(sys.argv) > 1:
        server_ip = sys.argv[1]
        port = int(sys.argv[2]) if len(sys.argv) > 2 else PORT
        print(f"Conectando ao servidor em {server_ip}:{port}...")
        client = GameClient(is_host=False, server_ip=server_ip)
    else:
        print("Iniciando como host...")
        client = GameClient(is_host=True)

if __name__ == "__main__":
    main()