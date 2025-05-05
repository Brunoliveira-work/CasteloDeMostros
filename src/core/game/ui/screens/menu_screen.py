import pyxel

class MenuScreen:
    def __init__(self, game_client):
        self.game_client = game_client
        self.menu_options = ["Host", "Join", "Exit"]
        self.selected_option = 0
    
    def update(self):
        """Update menu state"""
        if pyxel.btnp(pyxel.KEY_UP):
            self.selected_option = (self.selected_option - 1) % len(self.menu_options)
        elif pyxel.btnp(pyxel.KEY_DOWN):
            self.selected_option = (self.selected_option + 1) % len(self.menu_options)
        
        if pyxel.btnp(pyxel.KEY_RETURN):
            if self.menu_options[self.selected_option] == "Host":
                self.game_client.start_host()
            elif self.menu_options[self.selected_option] == "Join":
                self.game_client.show_join_screen()  # This now exists
            elif self.menu_options[self.selected_option] == "Exit":
                self.game_client.close()
    
    def draw(self):
        """Draw menu"""
        pyxel.text(100, 50, "Dino Multiplayer Clone", 7)
        for i, option in enumerate(self.menu_options):
            color = 11 if i == self.selected_option else 7
            pyxel.text(100, 100 + i * 20, option, color)
        pyxel.text(50, 220, "Use ↑↓ para navegar, ENTER para selecionar", 8)