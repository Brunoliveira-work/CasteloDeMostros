# src/core/game/ui/hud.py
import pyxel

class HUD:
    @staticmethod
    def draw(score: int, speed: float, is_paused: bool):
        pyxel.text(10, 10, f"SCORE: {score}", 0)
        pyxel.text(10, 20, f"SPEED: {speed:.1f}x", 0)
        if is_paused:
            pyxel.text(120, 100, "GAME OVER", pyxel.COLOR_RED)