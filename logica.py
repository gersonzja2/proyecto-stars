import pygame
import math
import random

# Inicializar pygame
pygame.init()

# Constantes del juego
ANCHO_VENTANA = 1000
ALTO_VENTANA = 700
FPS = 60

# Colores
NEGRO = (0, 0, 0)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
AZUL = (0, 0, 255)
AMARILLO = (255, 255, 0)
GRIS = (128, 128, 128)
MARRON = (139, 69, 19)
VERDE_OSCURO = (0, 100, 0)

class Tanque:
    def __init__(self, x, y, color, teclas):
        self.x = x
        self.y = y
        self.ancho = 30
        self.alto = 30
        self.color = color
        self.velocidad = 3
        self.angulo = 0
        self.teclas = teclas  # Diccionario con las teclas de control
        self.vidas = 3
        self.puntuacion = 0
        
    def mover(self, teclas_presionadas, obstaculos):
        # Calcular nueva posición
        nueva_x = self.x
        nueva_y = self.y
        
        if teclas_presionadas[self.teclas['arriba']]:
            nueva_y -= self.velocidad
        if teclas_presionadas[self.teclas['abajo']]:
            nueva_y += self.velocidad
        if teclas_presionadas[self.teclas['izquierda']]:
            nueva_x -= self.velocidad
        if teclas_presionadas[self.teclas['derecha']]:
            nueva_x += self.velocidad
            
        # Verificar colisiones con obstáculos no destructibles
        rect_tanque = pygame.Rect(nueva_x, nueva_y, self.ancho, self.alto)
        colision = False
        
        for obstaculo in obstaculos:
            if not obstaculo.destructible:
                if rect_tanque.colliderect(obstaculo.rect):
                    colision = True
                    break
                    
        # Verificar límites de la pantalla
        if (nueva_x < 0 or nueva_x > ANCHO_VENTANA - self.ancho or 
            nueva_y < 0 or nueva_y > ALTO_VENTANA - self.alto):
            colision = True
            
        # Solo mover si no hay colisión
        if not colision:
            self.x = nueva_x
            self.y = nueva_y
            
    def apuntar_hacia_mouse(self, mouse_pos):
        dx = mouse_pos[0] - (self.x + self.ancho // 2)
        dy = mouse_pos[1] - (self.y + self.alto // 2)
        self.angulo = math.atan2(dy, dx)
        
    def disparar(self):
        # Calcular posición de salida del cañón
        cañon_x = self.x + self.ancho // 2 + math.cos(self.angulo) * 25
        cañon_y = self.y + self.alto // 2 + math.sin(self.angulo) * 25
        
        return Bala(cañon_x, cañon_y, self.angulo, self.color)
        
    def dibujar(self, pantalla):
        # Dibujar cuerpo del tanque
        pygame.draw.rect(pantalla, self.color, (self.x, self.y, self.ancho, self.alto))
        
        # Dibujar cañón
        cañon_x = self.x + self.ancho // 2 + math.cos(self.angulo) * 20
        cañon_y = self.y + self.alto // 2 + math.sin(self.angulo) * 20
        pygame.draw.line(pantalla, self.color, 
                        (self.x + self.ancho // 2, self.y + self.alto // 2),
                        (cañon_x, cañon_y), 5)
        
        # Dibujar vidas
        for i in range(self.vidas):
            pygame.draw.circle(pantalla, ROJO, 
                             (self.x + 5 + i * 8, self.y - 10), 3)

class Bala:
    def __init__(self, x, y, angulo, color):
        self.x = x
        self.y = y
        self.velocidad = 8
        self.angulo = angulo
        self.color = color
        self.radio = 3
        
    def mover(self):
        self.x += math.cos(self.angulo) * self.velocidad
        self.y += math.sin(self.angulo) * self.velocidad
        
    def esta_fuera_pantalla(self):
        return (self.x < 0 or self.x > ANCHO_VENTANA or 
                self.y < 0 or self.y > ALTO_VENTANA)
        
    def dibujar(self, pantalla):
        pygame.draw.circle(pantalla, self.color, (int(self.x), int(self.y)), self.radio)

class Obstaculo:
    def __init__(self, x, y, tipo):
        self.x = x
        self.y = y
        self.tipo = tipo  # 'arbusto' o 'roca'
        self.destructible = (tipo == 'arbusto')
        self.ancho = 40
        self.alto = 40
        self.rect = pygame.Rect(x, y, self.ancho, self.alto)
        
    def dibujar(self, pantalla):
        if self.tipo == 'arbusto':
            pygame.draw.rect(pantalla, VERDE_OSCURO, self.rect)
            # Dibujar detalles del arbusto
            pygame.draw.circle(pantalla, VERDE, 
                             (self.x + 10, self.y + 10), 8)
            pygame.draw.circle(pantalla, VERDE, 
                             (self.x + 30, self.y + 15), 10)
            pygame.draw.circle(pantalla, VERDE, 
                             (self.x + 20, self.y + 30), 7)
        else:  # roca
            pygame.draw.rect(pantalla, GRIS, self.rect)
            # Dibujar detalles de la roca
            pygame.draw.polygon(pantalla, (100, 100, 100), 
                              [(self.x + 5, self.y + 35), (self.x + 15, self.y + 5),
                               (self.x + 35, self.y + 10), (self.x + 30, self.y + 35)])

class Juego:
    def __init__(self):
        self.pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        pygame.display.set_caption("Juego de Tanques")
        self.reloj = pygame.time.Clock()
        
        # Crear tanques
        self.tanque1 = Tanque(100, 100, AZUL, {
            'arriba': pygame.K_w,
            'abajo': pygame.K_s,
            'izquierda': pygame.K_a,
            'derecha': pygame.K_d
        })
        
        self.tanque2 = Tanque(800, 500, ROJO, {
            'arriba': pygame.K_i,
            'abajo': pygame.K_k,
            'izquierda': pygame.K_j,
            'derecha': pygame.K_l
        })
        
        # Listas de objetos del juego
        self.balas = []
        self.obstaculos = []
        
        # Crear obstáculos
        self.crear_obstaculos()
        
        # Fuente para texto
        self.fuente = pygame.font.Font(None, 36)
        
    def crear_obstaculos(self):
        # Crear rocas (no destructibles)
        posiciones_rocas = [
            (200, 200), (400, 150), (600, 300), (300, 400),
            (700, 200), (150, 500), (500, 500), (800, 400)
        ]
        
        for pos in posiciones_rocas:
            self.obstaculos.append(Obstaculo(pos[0], pos[1], 'roca'))
            
        # Crear arbustos (destructibles)
        posiciones_arbustos = [
            (250, 250), (350, 350), (450, 250), (550, 450),
            (650, 150), (750, 350), (150, 350), (850, 250)
        ]
        
        for pos in posiciones_arbustos:
            self.obstaculos.append(Obstaculo(pos[0], pos[1], 'arbusto'))
    
    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    # Tanque 1 dispara
                    self.balas.append(self.tanque1.disparar())
                elif evento.key == pygame.K_RETURN:
                    # Tanque 2 dispara
                    self.balas.append(self.tanque2.disparar())
        return True
    
    def actualizar(self):
        teclas_presionadas = pygame.key.get_pressed()
        
        # Mover tanques
        self.tanque1.mover(teclas_presionadas, self.obstaculos)
        self.tanque2.mover(teclas_presionadas, self.obstaculos)
        
        # Apuntar tanques hacia el mouse
        mouse_pos = pygame.mouse.get_pos()
        self.tanque1.apuntar_hacia_mouse(mouse_pos)
        self.tanque2.apuntar_hacia_mouse(mouse_pos)
        
        # Mover balas
        for bala in self.balas[:]:
            bala.mover()
            if bala.esta_fuera_pantalla():
                self.balas.remove(bala)
        
        # Verificar colisiones de balas
        self.verificar_colisiones()
    
    def verificar_colisiones(self):
        for bala in self.balas[:]:
            # Colisión con obstáculos
            for obstaculo in self.obstaculos[:]:
                if (obstaculo.rect.collidepoint(bala.x, bala.y)):
                    if obstaculo.destructible:
                        self.obstaculos.remove(obstaculo)
                    self.balas.remove(bala)
                    break
            
            # Colisión con tanques
            if (bala not in self.balas):
                continue
                
            # Verificar colisión con tanque 1
            if (self.tanque1.x < bala.x < self.tanque1.x + self.tanque1.ancho and
                self.tanque1.y < bala.y < self.tanque1.y + self.tanque1.alto):
                if bala.color != self.tanque1.color:
                    self.tanque1.vidas -= 1
                    self.tanque2.puntuacion += 10
                    self.balas.remove(bala)
                    
            # Verificar colisión con tanque 2
            elif (self.tanque2.x < bala.x < self.tanque2.x + self.tanque2.ancho and
                  self.tanque2.y < bala.y < self.tanque2.y + self.tanque2.alto):
                if bala.color != self.tanque2.color:
                    self.tanque2.vidas -= 1
                    self.tanque1.puntuacion += 10
                    self.balas.remove(bala)
    
    def dibujar(self):
        self.pantalla.fill(NEGRO)
        
        # Dibujar obstáculos
        for obstaculo in self.obstaculos:
            obstaculo.dibujar(self.pantalla)
        
        # Dibujar tanques
        self.tanque1.dibujar(self.pantalla)
        self.tanque2.dibujar(self.pantalla)
        
        # Dibujar balas
        for bala in self.balas:
            bala.dibujar(self.pantalla)
        
        # Dibujar información del juego
        texto_puntuacion1 = self.fuente.render(f"Tanque Azul: {self.tanque1.puntuacion}", True, AZUL)
        texto_puntuacion2 = self.fuente.render(f"Tanque Rojo: {self.tanque2.puntuacion}", True, ROJO)
        
        self.pantalla.blit(texto_puntuacion1, (10, 10))
        self.pantalla.blit(texto_puntuacion2, (10, 50))
        
        # Instrucciones
        instrucciones = [
            "Controles:",
            "Tanque Azul: WASD para mover, ESPACIO para disparar",
            "Tanque Rojo: IJKL para mover, ENTER para disparar",
            "Mouse para apuntar"
        ]
        
        for i, instruccion in enumerate(instrucciones):
            texto = pygame.font.Font(None, 24).render(instruccion, True, AMARILLO)
            self.pantalla.blit(texto, (10, ALTO_VENTANA - 100 + i * 20))
        
        pygame.display.flip()
    
    def ejecutar(self):
        ejecutando = True
        while ejecutando:
            ejecutando = self.manejar_eventos()
            self.actualizar()
            self.dibujar()
            self.reloj.tick(FPS)
            
            # Verificar fin del juego
            if self.tanque1.vidas <= 0 or self.tanque2.vidas <= 0:
                ejecutando = False
                
        pygame.quit()

if __name__ == "__main__":
    juego = Juego()
    juego.ejecutar()
