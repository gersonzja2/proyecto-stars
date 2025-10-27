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

class DestelloDisparo(Efecto):
    """Un destello en forma de estrella en la boca del cañón al disparar."""
    def __init__(self, x, y, angulo):
        super().__init__(x, y, 6) # Duración muy corta
        self.angulo = angulo
        self.color = s.BLANCO_BRILLANTE
        self.longitud = 15

    def dibujar(self, pantalla):
        progreso = self.get_progreso()
        longitud_actual = self.longitud * (1 - progreso)
        if longitud_actual > 0:
            # Dibuja una forma de estrella/cruz
            p1 = (self.x + math.cos(self.angulo) * longitud_actual, self.y + math.sin(self.angulo) * longitud_actual)
            p2 = (self.x - math.cos(self.angulo) * longitud_actual, self.y - math.sin(self.angulo) * longitud_actual)
            p3 = (self.x + math.cos(self.angulo + math.pi/2) * longitud_actual / 2, self.y + math.sin(self.angulo + math.pi/2) * longitud_actual / 2)
            p4 = (self.x - math.cos(self.angulo + math.pi/2) * longitud_actual / 2, self.y - math.sin(self.angulo + math.pi/2) * longitud_actual / 2)
            
            # El alpha se puede aplicar directamente en el color si la superficie lo soporta.
            # Pygame > 2.0.0 lo maneja bien en la mayoría de los casos.
            color = self.color
            pygame.draw.line(pantalla, color, p1, p2, 3)
            pygame.draw.line(pantalla, color, p3, p4, 3)

class Chispas(Particula):
    """Partículas de chispas que se generan al impactar superficies duras."""
    def __init__(self, x, y, dx, dy):
        super().__init__(x, y, dx, dy, s.AMARILLO)
        self.max_tiempo = random.randint(15, 25) # Las chispas duran menos
        self.radio = random.randint(1, 3)

    def actualizar(self):
        super().actualizar()
        # Las chispas no tienen tanta fricción y caen más rápido
        self.dy += 0.25
        self.dx *= 0.98
        self.dy *= 0.98

    def dibujar(self, pantalla):
        # Las chispas son líneas en lugar de círculos para dar sensación de velocidad
        x2 = self.x - self.dx * 2
        y2 = self.y - self.dy * 2
        pygame.draw.line(pantalla, self.color, (self.x, self.y), (x2, y2), self.radio)