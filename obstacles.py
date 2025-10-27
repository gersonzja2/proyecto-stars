import pygame

class Obstaculo:
    """Clase base para todos los obstáculos del juego."""
    def __init__(self, x, y, salud=1, destructible=False):
        self.x = x
        self.y = y
        self.ancho = 40
        self.alto = 40
        self.rect = pygame.Rect(x, y, self.ancho, self.alto)
        self.salud = salud
        self.salud_max = self.salud
        self.destructible = destructible

    def recibir_daño(self):
        """Reduce la salud del obstáculo si es destructible. Devuelve True si se destruye."""
        if self.destructible:
            self.salud -= 1
            return self.salud <= 0
        return False

class Roca(Obstaculo):
    def __init__(self, x, y):
        super().__init__(x, y, salud=999, destructible=False)

class Arbusto(Obstaculo):
    def __init__(self, x, y):
        super().__init__(x, y, salud=2, destructible=True)

class Muro(Obstaculo):
    def __init__(self, x, y):
        super().__init__(x, y, salud=5, destructible=True)

class CajaMadera(Obstaculo):
    def __init__(self, x, y):
        super().__init__(x, y, salud=3, destructible=True)