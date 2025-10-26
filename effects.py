import pygame
import math
import random
import settings as s

class Efecto:
    """Clase base para todos los efectos visuales."""
    
    def __init__(self, x, y, max_tiempo):
        self.x = x
        self.y = y
        self.tiempo = 0
        self.max_tiempo = max_tiempo

    def actualizar(self):
        """Actualiza el estado del efecto en cada frame."""
        self.tiempo += 1

    def dibujar(self, pantalla):
        """Dibuja el efecto en la pantalla. Debe ser implementado por las subclases."""
        pass

    def ha_terminado(self):
        """Devuelve True si el efecto ha completado su ciclo de vida."""
        return self.tiempo >= self.max_tiempo

    def get_progreso(self):
        """Devuelve el progreso del efecto como un float de 0.0 a 1.0."""
        return self.tiempo / self.max_tiempo

class Explosion(Efecto):
    """Un círculo que se expande rápidamente y se desvanece, simulando una explosión."""
    def __init__(self, x, y):
        super().__init__(x, y, s.DURACION_EXPLOSION)
        self.radio = 0
        self.max_radio = 25
        self.color = s.AMARILLO_FUEGO

    def actualizar(self):
        super().actualizar()
        progreso = self.get_progreso()
        # Fórmula de "ease-out" para que la expansión sea rápida al inicio y lenta al final.
        self.radio = int((1 - (1 - progreso) ** 2) * self.max_radio)

    def dibujar(self, pantalla):
        progreso = self.get_progreso()
        # La opacidad (alpha) disminuye a medida que el efecto envejece.
        alpha = int(200 * (1 - progreso))
        if alpha > 0:
            surf = pygame.Surface((self.radio * 2, self.radio * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (self.radio, self.radio), self.radio)
            pygame.draw.circle(surf, (*s.BLANCO_BRILLANTE, alpha // 2), (self.radio, self.radio), max(1, self.radio - 2))
            pantalla.blit(surf, (int(self.x) - self.radio, int(self.y) - self.radio))

class Onda(Efecto):
    """Una onda expansiva circular que se desvanece."""
    def __init__(self, x, y):
        super().__init__(x, y, s.DURACION_EXPLOSION)
        self.radio = 5
        self.max_radio = 40
        self.color = s.BLANCO_BRILLANTE

    def actualizar(self):
        super().actualizar()
        self.radio = int(self.get_progreso() * self.max_radio)

    def dibujar(self, pantalla):
        progreso = self.get_progreso()
        alpha = int(100 * (1 - progreso))
        if alpha > 0 and self.radio > 0:
            surf = pygame.Surface((self.radio * 2, self.radio * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (self.radio, self.radio), self.radio, 2)
            pantalla.blit(surf, (int(self.x) - self.radio, int(self.y) - self.radio))

class Destello(Efecto):
    """Un destello brillante y corto que se encoge rápidamente."""
    def __init__(self, x, y):
        super().__init__(x, y, s.DURACION_DESTELLO)
        self.radio_inicial = 12
        self.radio = self.radio_inicial
        self.color = s.BLANCO_BRILLANTE

    def actualizar(self):
        super().actualizar()
        self.radio = int(self.radio_inicial * (1 - self.get_progreso()))

    def dibujar(self, pantalla):
        progreso = self.get_progreso()
        alpha = int(200 * (1 - progreso))
        if alpha > 0 and self.radio > 0:
            surf = pygame.Surface((self.radio * 2, self.radio * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (self.radio, self.radio), self.radio)
            pantalla.blit(surf, (int(self.x) - self.radio, int(self.y) - self.radio))

class Particula(Efecto):
    """Una pequeña partícula que se mueve con física simple (gravedad y fricción)."""
    def __init__(self, x, y, dx, dy, color):
        super().__init__(x, y, s.DURACION_EXPLOSION)
        self.dx = dx
        self.dy = dy
        self.radio = random.randint(2, 4)
        self.color = color

    def actualizar(self):
        super().actualizar()
        self.x += self.dx
        self.y += self.dy
        self.dy += 0.15  # Gravedad
        self.dx *= 0.95  # Fricción
        self.dy *= 0.95

    def dibujar(self, pantalla):
        alpha = int(200 * (1 - self.get_progreso()))
        if alpha > 0:
            surf = pygame.Surface((self.radio * 2, self.radio * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (self.radio, self.radio), self.radio)
            pantalla.blit(surf, (int(self.x) - self.radio, int(self.y) - self.radio))

class Humo(Efecto):
    """Una partícula de humo que se expande y se desvanece lentamente."""
    def __init__(self, x, y, dx, dy):
        super().__init__(x, y, s.DURACION_EXPLOSION)
        self.dx = dx
        self.dy = dy
        self.radio_inicial = random.randint(3, 6)
        self.radio = self.radio_inicial
        self.color = s.GRIS
        self.opacidad_inicial = random.randint(100, 180)

    def actualizar(self):
        super().actualizar()
        self.x += self.dx
        self.y += self.dy
        self.radio = int(self.radio_inicial * (1 + self.get_progreso() * 0.5))
        self.dx *= 0.98
        self.dy *= 0.98

    def dibujar(self, pantalla):
        opacidad = int(self.opacidad_inicial * (1 - self.get_progreso()))
        if opacidad > 0:
            surf = pygame.Surface((self.radio * 2, self.radio * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, opacidad), (self.radio, self.radio), self.radio)
            pantalla.blit(surf, (int(self.x) - self.radio, int(self.y) - self.radio))

class Rastro(Efecto):
    """Un rastro visual dejado por los tanques al moverse."""
    def __init__(self, x, y, color):
        super().__init__(x, y, 20) # max_tiempo
        self.radio = 3
        self.color = color

    def dibujar(self, pantalla):
        opacidad = int(255 * (1 - self.get_progreso()))
        if opacidad > 0:
            surf = pygame.Surface((self.radio * 2, self.radio * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, opacidad), (self.radio, self.radio), self.radio)
            pantalla.blit(surf, (int(self.x) - self.radio, int(self.y) - self.radio))