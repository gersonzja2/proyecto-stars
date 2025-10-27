import pygame
import math
import random
import settings as s
import effects

class Tanque:
    """Representa un tanque jugador, con su lógica de movimiento, disparo y estado."""
    def __init__(self, x, y, color, teclas, juego):
        self.x = x
        self.y = y
        self.ancho = 30
        self.alto = 30
        self.color = color
        self.velocidad = 4
        self.angulo = 0
        self.teclas = teclas  # Diccionario con las teclas de control
        self.vidas = 3
        self.puntuacion = 0
        self.rect = pygame.Rect(x, y, self.ancho, self.alto)
        self.ultimo_disparo = 0
        self.velocidad_disparo = 500  # ms entre disparos
        self.invulnerable = False
        self.tiempo_invulnerable = 0
        self.juego = juego  # Referencia al juego para efectos de sonido
        self.motor_sonando = False
        self.ultimo_rastro = 0
        self.tiempo_entre_rastros = 50  # ms entre efectos de rastro
        
    def mover(self, teclas_presionadas, obstaculos, otros_tanques):
        """
        Maneja la lógica de movimiento y rotación del tanque.
        - Rota el tanque según las teclas de izquierda/derecha.
        - Avanza en la dirección del ángulo actual.
        - Realiza detección de colisiones con bordes, obstáculos y otros tanques.
        - Crea efectos de sonido y rastro al moverse.
        - Devuelve True si el tanque debe disparar (al avanzar).
        """
        # Sistema de rotación y movimiento direccional
        nueva_x = self.x
        nueva_y = self.y
        movimiento_x = 0
        movimiento_y = 0
        disparar = False
        
        # Rotación con teclas de dirección
        if teclas_presionadas[self.teclas['izquierda']]:
            self.angulo -= 0.1  # Rotar hacia la izquierda
        if teclas_presionadas[self.teclas['derecha']]:
            self.angulo += 0.1  # Rotar hacia la derecha
        
        # Movimiento hacia adelante con tecla de avance
        tiempo_actual = pygame.time.get_ticks()
        if teclas_presionadas[self.teclas['avanzar']]:
            movimiento_x = math.cos(self.angulo) * self.velocidad
            movimiento_y = math.sin(self.angulo) * self.velocidad
            disparar = True  # Disparar automáticamente al moverse
            
            # Efecto de sonido del motor
            if 'motor' in self.juego.assets.sounds and not self.motor_sonando:
                self.juego.assets.sounds['motor'].play(-1)  # Loop continuo
                self.motor_sonando = True
                
            # Crear efecto de rastro
            if tiempo_actual - self.ultimo_rastro >= self.tiempo_entre_rastros:
                self.juego.efectos.append(effects.Rastro(self.x + self.ancho//2, self.y + self.alto//2, self.color))
                self.ultimo_rastro = tiempo_actual

            # Crear efecto de humo si el tanque está dañado
            if self.vidas == 1 and tiempo_actual - self.ultimo_rastro >= self.tiempo_entre_rastros * 2:
                angulo_humo = self.angulo + random.uniform(-0.5, 0.5) + math.pi # Hacia atrás
                self.juego.efectos.append(effects.Humo(self.x + self.ancho//2, self.y + self.alto//2, math.cos(angulo_humo)*0.5, math.sin(angulo_humo)*0.5))

        else:
            # Detener sonido del motor
            if self.motor_sonando and 'motor' in self.juego.assets.sounds:
                self.juego.assets.sounds['motor'].stop()
                self.motor_sonando = False
            
        nueva_x += movimiento_x
        nueva_y += movimiento_y
            
        # Verificar colisiones con obstáculos (todos los obstáculos son sólidos)
        rect_tanque = pygame.Rect(nueva_x, nueva_y, self.ancho, self.alto)
        colision = False
        
        # Colisión con obstáculos (tanto destructibles como no destructibles)
        for obstaculo in obstaculos:
            if rect_tanque.colliderect(obstaculo.rect):
                colision = True
                break
                
        # Colisión con otros tanques
        for tanque in otros_tanques:
            if tanque != self and rect_tanque.colliderect(tanque.rect):
                colision = True
                break
                    
        # Verificar límites de la pantalla (más estricto)
        if (nueva_x < 0 or nueva_x >= s.ANCHO_VENTANA - self.ancho or 
            nueva_y < 0 or nueva_y >= s.ALTO_VENTANA - self.alto):
            colision = True
            
        # Verificar que no entre en la zona de la interfaz superior (primeros 80 píxeles)
        if nueva_y < 80:
            colision = True
            
        # Solo mover si no hay colisión
        if not colision:
            self.x = nueva_x
            self.y = nueva_y
            self.rect.x = self.x
            self.rect.y = self.y
            
        return disparar  # Devolver si debe disparar

    def disparar(self, Bala):
        """
        Crea un objeto Bala si ha pasado suficiente tiempo desde el último disparo.
        Devuelve el objeto Bala o None.
        """
        tiempo_actual = pygame.time.get_ticks()
        # Controla la cadencia de disparo.
        if tiempo_actual - self.ultimo_disparo >= self.velocidad_disparo:
            # Calcular posición de salida del cañón
            # La bala se crea un poco más adelante del tanque, en la dirección del cañón.
            cañon_x = self.x + self.ancho // 2 + math.cos(self.angulo) * 25
            cañon_y = self.y + self.alto // 2 + math.sin(self.angulo) * 25
            
            self.ultimo_disparo = tiempo_actual
            # Reproducir sonido de disparo si está disponible
            if 'disparo' in self.juego.assets.sounds:
                self.juego.assets.sounds['disparo'].play()
            
            # Crear efecto de destello de disparo
            self.juego.efectos.append(effects.DestelloDisparo(cañon_x, cañon_y, self.angulo))

            return Bala(cañon_x, cañon_y, self.angulo, self.color)
        return None