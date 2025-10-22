import pygame
import math
import random
import time

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
BLANCO = (255, 255, 255)
NARANJA = (255, 165, 0)
MORADO = (128, 0, 128)
VERDE_CLARO = (144, 238, 144)
GRIS_CLARO = (200, 200, 200)

class Tanque:
    def __init__(self, x, y, color, teclas):
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
        
    def mover(self, teclas_presionadas, obstaculos, otros_tanques):
        # Calcular nueva posición con movimiento diagonal suavizado
        nueva_x = self.x
        nueva_y = self.y
        movimiento_x = 0
        movimiento_y = 0
        
        if teclas_presionadas[self.teclas['arriba']]:
            movimiento_y -= self.velocidad
        if teclas_presionadas[self.teclas['abajo']]:
            movimiento_y += self.velocidad
        if teclas_presionadas[self.teclas['izquierda']]:
            movimiento_x -= self.velocidad
        if teclas_presionadas[self.teclas['derecha']]:
            movimiento_x += self.velocidad
            
        # Normalizar movimiento diagonal
        if movimiento_x != 0 and movimiento_y != 0:
            movimiento_x *= 0.707  # 1/sqrt(2)
            movimiento_y *= 0.707
            
        nueva_x += movimiento_x
        nueva_y += movimiento_y
            
        # Verificar colisiones con obstáculos no destructibles
        rect_tanque = pygame.Rect(nueva_x, nueva_y, self.ancho, self.alto)
        colision = False
        
        # Colisión con obstáculos
        for obstaculo in obstaculos:
            if not obstaculo.destructible and rect_tanque.colliderect(obstaculo.rect):
                colision = True
                break
                
        # Colisión con otros tanques
        for tanque in otros_tanques:
            if tanque != self and rect_tanque.colliderect(tanque.rect):
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
            self.rect.x = self.x
            self.rect.y = self.y
            
    def apuntar_hacia_mouse(self, mouse_pos):
        dx = mouse_pos[0] - (self.x + self.ancho // 2)
        dy = mouse_pos[1] - (self.y + self.alto // 2)
        self.angulo = math.atan2(dy, dx)
        
    def disparar(self):
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.ultimo_disparo >= self.velocidad_disparo:
            # Calcular posición de salida del cañón
            cañon_x = self.x + self.ancho // 2 + math.cos(self.angulo) * 25
            cañon_y = self.y + self.alto // 2 + math.sin(self.angulo) * 25
            
            self.ultimo_disparo = tiempo_actual
            return Bala(cañon_x, cañon_y, self.angulo, self.color)
        return None
        
    def dibujar(self, pantalla):
        # Efecto de invulnerabilidad (parpadeo)
        tiempo_actual = pygame.time.get_ticks()
        if self.invulnerable and (tiempo_actual // 100) % 2:
            return  # Parpadeo durante invulnerabilidad
            
        # Dibujar cuerpo del tanque con gradiente
        pygame.draw.rect(pantalla, self.color, (self.x, self.y, self.ancho, self.alto))
        pygame.draw.rect(pantalla, BLANCO, (self.x + 2, self.y + 2, self.ancho - 4, self.alto - 4), 2)
        
        # Dibujar cañón
        cañon_x = self.x + self.ancho // 2 + math.cos(self.angulo) * 20
        cañon_y = self.y + self.alto // 2 + math.sin(self.angulo) * 20
        pygame.draw.line(pantalla, self.color, 
                        (self.x + self.ancho // 2, self.y + self.alto // 2),
                        (cañon_x, cañon_y), 5)
        
        # Dibujar vidas con mejor representación
        for i in range(self.vidas):
            color_vida = ROJO if i < self.vidas else GRIS
            pygame.draw.circle(pantalla, color_vida, 
                             (int(self.x + 5 + i * 8), int(self.y - 10)), 4)
            pygame.draw.circle(pantalla, BLANCO, 
                             (int(self.x + 5 + i * 8), int(self.y - 10)), 4, 1)

class Bala:
    def __init__(self, x, y, angulo, color):
        self.x = x
        self.y = y
        self.velocidad = 10
        self.angulo = angulo
        self.color = color
        self.radio = 4
        self.rect = pygame.Rect(x - self.radio, y - self.radio, self.radio * 2, self.radio * 2)
        self.tiempo_vida = 0
        self.tiempo_max_vida = 3000  # 3 segundos
        
    def mover(self):
        self.x += math.cos(self.angulo) * self.velocidad
        self.y += math.sin(self.angulo) * self.velocidad
        self.rect.x = self.x - self.radio
        self.rect.y = self.y - self.radio
        self.tiempo_vida += 16  # Aproximadamente 60 FPS
        
    def esta_fuera_pantalla(self):
        return (self.x < -10 or self.x > ANCHO_VENTANA + 10 or 
                self.y < -10 or self.y > ALTO_VENTANA + 10)
                
    def tiempo_agotado(self):
        return self.tiempo_vida >= self.tiempo_max_vida
        
    def dibujar(self, pantalla):
        # Dibujar bala con efecto de brillo
        pygame.draw.circle(pantalla, self.color, (int(self.x), int(self.y)), self.radio)
        pygame.draw.circle(pantalla, BLANCO, (int(self.x), int(self.y)), self.radio - 1, 1)
        # Efecto de estela
        pygame.draw.circle(pantalla, self.color, (int(self.x - math.cos(self.angulo) * 5), 
                                                 int(self.y - math.sin(self.angulo) * 5)), 2)

class Obstaculo:
    def __init__(self, x, y, tipo):
        self.x = x
        self.y = y
        self.tipo = tipo  # 'arbusto' o 'roca'
        self.destructible = (tipo == 'arbusto')
        self.ancho = 40
        self.alto = 40
        self.rect = pygame.Rect(x, y, self.ancho, self.alto)
        self.salud = 2 if self.destructible else 999
        self.salud_max = self.salud
        
    def recibir_daño(self):
        if self.destructible:
            self.salud -= 1
            return self.salud <= 0
        return False
        
    def dibujar(self, pantalla):
        if self.tipo == 'arbusto':
            # Base del arbusto
            pygame.draw.rect(pantalla, MARRON, (self.x + 15, self.y + 30, 10, 10))
            
            # Hojas del arbusto con gradiente
            color_verde = VERDE_OSCURO if self.salud == self.salud_max else VERDE_CLARO
            pygame.draw.circle(pantalla, color_verde, (self.x + 8, self.y + 8), 12)
            pygame.draw.circle(pantalla, color_verde, (self.x + 32, self.y + 12), 14)
            pygame.draw.circle(pantalla, color_verde, (self.x + 20, self.y + 25), 10)
            pygame.draw.circle(pantalla, color_verde, (self.x + 12, self.y + 20), 8)
            pygame.draw.circle(pantalla, color_verde, (self.x + 28, self.y + 28), 9)
            
            # Efecto de daño
            if self.salud < self.salud_max:
                pygame.draw.circle(pantalla, ROJO, (self.x + 20, self.y + 20), 3)
                
        else:  # roca
            # Base de la roca
            pygame.draw.rect(pantalla, GRIS, self.rect)
            pygame.draw.rect(pantalla, GRIS_CLARO, (self.x + 2, self.y + 2, self.ancho - 4, self.alto - 4))
            
            # Detalles de la roca
            pygame.draw.polygon(pantalla, (80, 80, 80), 
                              [(self.x + 5, self.y + 35), (self.x + 15, self.y + 5),
                               (self.x + 35, self.y + 10), (self.x + 30, self.y + 35)])
            pygame.draw.polygon(pantalla, (60, 60, 60), 
                              [(self.x + 10, self.y + 30), (self.x + 20, self.y + 15),
                               (self.x + 30, self.y + 20), (self.x + 25, self.y + 32)])
            
            # Sombras
            pygame.draw.line(pantalla, (40, 40, 40), (self.x, self.y + 35), (self.x + 40, self.y + 35), 2)

class Juego:
    def __init__(self):
        self.pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        pygame.display.set_caption("Juego de Tanques - Optimizado")
        self.reloj = pygame.time.Clock()
        
        # Inicializar música
        self.inicializar_musica()
        
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
        self.efectos = []  # Para efectos visuales
        
        # Crear obstáculos
        self.crear_obstaculos()
        
        # Fuentes para texto
        self.fuente_grande = pygame.font.Font(None, 48)
        self.fuente = pygame.font.Font(None, 36)
        self.fuente_pequeña = pygame.font.Font(None, 24)
        
        # Estado del juego
        self.juego_terminado = False
        self.ganador = None
        self.musica_pausada = False
        self.volumen_actual = 0.3
        
    def inicializar_musica(self):
        """Inicializa y reproduce la música de fondo."""
        try:
            # Inicializar el mixer de pygame
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            
            # Cargar y reproducir la música de fondo
            pygame.mixer.music.load("megalovia.mp3")
            pygame.mixer.music.set_volume(0.3)  # Volumen al 30%
            pygame.mixer.music.play(-1)  # -1 para reproducir en loop infinito
            
            print("Música de fondo cargada correctamente")
        except pygame.error as e:
            print(f"Error al cargar la música: {e}")
            print("El juego continuará sin música de fondo")
        except FileNotFoundError:
            print("Archivo megalovia.mp3 no encontrado")
            print("El juego continuará sin música de fondo")
    
    def toggle_musica(self):
        """Pausa o reanuda la música de fondo."""
        try:
            if self.musica_pausada:
                pygame.mixer.music.unpause()
                self.musica_pausada = False
                print("Música reanudada")
            else:
                pygame.mixer.music.pause()
                self.musica_pausada = True
                print("Música pausada")
        except pygame.error:
            print("Error al controlar la música")
    
    def aumentar_volumen(self):
        """Aumenta el volumen de la música."""
        if self.volumen_actual < 1.0:
            self.volumen_actual = min(1.0, self.volumen_actual + 0.1)
            pygame.mixer.music.set_volume(self.volumen_actual)
            print(f"Volumen: {int(self.volumen_actual * 100)}%")
    
    def disminuir_volumen(self):
        """Disminuye el volumen de la música."""
        if self.volumen_actual > 0.0:
            self.volumen_actual = max(0.0, self.volumen_actual - 0.1)
            pygame.mixer.music.set_volume(self.volumen_actual)
            print(f"Volumen: {int(self.volumen_actual * 100)}%")
        
    def crear_obstaculos(self):
        # Crear rocas (no destructibles) - más estratégicamente colocadas
        posiciones_rocas = [
            (200, 200), (400, 150), (600, 300), (300, 400),
            (700, 200), (150, 500), (500, 500), (800, 400),
            (350, 250), (650, 450), (250, 600), (750, 100)
        ]
        
        for pos in posiciones_rocas:
            self.obstaculos.append(Obstaculo(pos[0], pos[1], 'roca'))
            
        # Crear arbustos (destructibles) - más distribuidos
        posiciones_arbustos = [
            (250, 250), (350, 350), (450, 250), (550, 450),
            (650, 150), (750, 350), (150, 350), (850, 250),
            (100, 200), (300, 100), (500, 400), (700, 500),
            (200, 450), (400, 300), (600, 200), (800, 150)
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
                    bala = self.tanque1.disparar()
                    if bala:
                        self.balas.append(bala)
                elif evento.key == pygame.K_RETURN:
                    # Tanque 2 dispara
                    bala = self.tanque2.disparar()
                    if bala:
                        self.balas.append(bala)
                elif evento.key == pygame.K_r and self.juego_terminado:
                    # Reiniciar juego
                    self.reiniciar_juego()
                elif evento.key == pygame.K_m:
                    # Pausar/reanudar música
                    self.toggle_musica()
                elif evento.key == pygame.K_PLUS or evento.key == pygame.K_EQUALS:
                    # Aumentar volumen
                    self.aumentar_volumen()
                elif evento.key == pygame.K_MINUS:
                    # Disminuir volumen
                    self.disminuir_volumen()
        return True
    
    def actualizar(self):
        if self.juego_terminado:
            return
            
        teclas_presionadas = pygame.key.get_pressed()
        
        # Mover tanques con detección de colisiones entre ellos
        otros_tanques = [self.tanque2] if self.tanque1.vidas > 0 else []
        self.tanque1.mover(teclas_presionadas, self.obstaculos, otros_tanques)
        
        otros_tanques = [self.tanque1] if self.tanque2.vidas > 0 else []
        self.tanque2.mover(teclas_presionadas, self.obstaculos, otros_tanques)
        
        # Apuntar tanques hacia el mouse
        mouse_pos = pygame.mouse.get_pos()
        if self.tanque1.vidas > 0:
            self.tanque1.apuntar_hacia_mouse(mouse_pos)
        if self.tanque2.vidas > 0:
            self.tanque2.apuntar_hacia_mouse(mouse_pos)
        
        # Mover balas
        for bala in self.balas[:]:
            bala.mover()
            if bala.esta_fuera_pantalla() or bala.tiempo_agotado():
                self.balas.remove(bala)
        
        # Verificar colisiones de balas
        self.verificar_colisiones()
        
        # Actualizar efectos de invulnerabilidad
        self.actualizar_invulnerabilidad()
        
        # Verificar fin del juego
        if self.tanque1.vidas <= 0 and self.tanque2.vidas <= 0:
            self.juego_terminado = True
            self.ganador = "Empate"
        elif self.tanque1.vidas <= 0:
            self.juego_terminado = True
            self.ganador = "Tanque Rojo"
        elif self.tanque2.vidas <= 0:
            self.juego_terminado = True
            self.ganador = "Tanque Azul"
    
    def verificar_colisiones(self):
        for bala in self.balas[:]:
            # Colisión con obstáculos usando rectángulos
            for obstaculo in self.obstaculos[:]:
                if bala.rect.colliderect(obstaculo.rect):
                    if obstaculo.destructible:
                        if obstaculo.recibir_daño():
                            self.obstaculos.remove(obstaculo)
                            # Efecto de destrucción
                            self.crear_efecto_explosion(obstaculo.x + 20, obstaculo.y + 20)
                    self.balas.remove(bala)
                    break
            
            # Colisión con tanques usando rectángulos
            if bala not in self.balas:
                continue
                
            # Verificar colisión con tanque 1
            if (self.tanque1.vidas > 0 and bala.rect.colliderect(self.tanque1.rect) and 
                bala.color != self.tanque1.color and not self.tanque1.invulnerable):
                self.tanque1.vidas -= 1
                self.tanque2.puntuacion += 10
                self.tanque1.invulnerable = True
                self.tanque1.tiempo_invulnerable = pygame.time.get_ticks()
                self.crear_efecto_explosion(self.tanque1.x + 15, self.tanque1.y + 15)
                self.balas.remove(bala)
                    
            # Verificar colisión con tanque 2
            elif (self.tanque2.vidas > 0 and bala.rect.colliderect(self.tanque2.rect) and 
                  bala.color != self.tanque2.color and not self.tanque2.invulnerable):
                self.tanque2.vidas -= 1
                self.tanque1.puntuacion += 10
                self.tanque2.invulnerable = True
                self.tanque2.tiempo_invulnerable = pygame.time.get_ticks()
                self.crear_efecto_explosion(self.tanque2.x + 15, self.tanque2.y + 15)
                self.balas.remove(bala)
    
    def actualizar_invulnerabilidad(self):
        """Actualiza el estado de invulnerabilidad de los tanques."""
        tiempo_actual = pygame.time.get_ticks()
        
        if self.tanque1.invulnerable and tiempo_actual - self.tanque1.tiempo_invulnerable > 2000:
            self.tanque1.invulnerable = False
            
        if self.tanque2.invulnerable and tiempo_actual - self.tanque2.tiempo_invulnerable > 2000:
            self.tanque2.invulnerable = False
    
    def crear_efecto_explosion(self, x, y):
        """Crea un efecto visual de explosión."""
        self.efectos.append({
            'x': x, 'y': y, 'tiempo': 0, 'max_tiempo': 30,
            'radio': 0, 'max_radio': 20
        })
    
    def actualizar_efectos(self):
        """Actualiza los efectos visuales."""
        for efecto in self.efectos[:]:
            efecto['tiempo'] += 1
            efecto['radio'] = int((efecto['tiempo'] / efecto['max_tiempo']) * efecto['max_radio'])
            
            if efecto['tiempo'] >= efecto['max_tiempo']:
                self.efectos.remove(efecto)
    
    def dibujar_efectos(self):
        """Dibuja los efectos visuales."""
        for efecto in self.efectos:
            alpha = int(255 * (1 - efecto['tiempo'] / efecto['max_tiempo']))
            color = (255, 100, 0, alpha)
            
            # Crear superficie con alpha
            surf = pygame.Surface((efecto['radio'] * 2, efecto['radio'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (efecto['radio'], efecto['radio']), efecto['radio'])
            self.pantalla.blit(surf, (efecto['x'] - efecto['radio'], efecto['y'] - efecto['radio']))
    
    def reiniciar_juego(self):
        """Reinicia el juego a su estado inicial."""
        self.tanque1 = Tanque(100, 100, AZUL, {
            'arriba': pygame.K_w, 'abajo': pygame.K_s,
            'izquierda': pygame.K_a, 'derecha': pygame.K_d
        })
        
        self.tanque2 = Tanque(800, 500, ROJO, {
            'arriba': pygame.K_i, 'abajo': pygame.K_k,
            'izquierda': pygame.K_j, 'derecha': pygame.K_l
        })
        
        self.balas = []
        self.efectos = []
        self.obstaculos = []
        self.crear_obstaculos()
        self.juego_terminado = False
        self.ganador = None
        # La música continúa reproduciéndose
    
    def dibujar(self):
        self.pantalla.fill(NEGRO)
        
        # Dibujar obstáculos
        for obstaculo in self.obstaculos:
            obstaculo.dibujar(self.pantalla)
        
        # Dibujar tanques
        if self.tanque1.vidas > 0:
            self.tanque1.dibujar(self.pantalla)
        if self.tanque2.vidas > 0:
            self.tanque2.dibujar(self.pantalla)
        
        # Dibujar balas
        for bala in self.balas:
            bala.dibujar(self.pantalla)
        
        # Dibujar efectos
        self.dibujar_efectos()
        
        # Dibujar información del juego
        self.dibujar_ui()
        
        # Dibujar pantalla de fin de juego
        if self.juego_terminado:
            self.dibujar_pantalla_fin()
        
        pygame.display.flip()
    
    def dibujar_ui(self):
        """Dibuja la interfaz de usuario."""
        # Panel de información
        pygame.draw.rect(self.pantalla, (50, 50, 50), (0, 0, ANCHO_VENTANA, 80))
        pygame.draw.line(self.pantalla, BLANCO, (0, 80), (ANCHO_VENTANA, 80), 2)
        
        # Puntuaciones
        texto_puntuacion1 = self.fuente.render(f"Tanque Azul: {self.tanque1.puntuacion}", True, AZUL)
        texto_puntuacion2 = self.fuente.render(f"Tanque Rojo: {self.tanque2.puntuacion}", True, ROJO)
        
        self.pantalla.blit(texto_puntuacion1, (10, 10))
        self.pantalla.blit(texto_puntuacion2, (10, 40))
        
        # Instrucciones
        instrucciones = [
            "WASD: Tanque Azul | IJKL: Tanque Rojo | ESPACIO/ENTER: Disparar | R: Reiniciar",
            "M: Pausar/Reanudar música | +/-: Ajustar volumen"
        ]
        
        for i, instruccion in enumerate(instrucciones):
            texto = self.fuente_pequeña.render(instruccion, True, AMARILLO)
            self.pantalla.blit(texto, (ANCHO_VENTANA - 600, 10 + i * 20))
        
        # Mostrar estado de la música
        estado_musica = "Música: ON" if not self.musica_pausada else "Música: OFF"
        color_musica = VERDE if not self.musica_pausada else ROJO
        texto_musica = self.fuente_pequeña.render(estado_musica, True, color_musica)
        self.pantalla.blit(texto_musica, (ANCHO_VENTANA - 200, 50))
        
        # Mostrar volumen
        texto_volumen = self.fuente_pequeña.render(f"Vol: {int(self.volumen_actual * 100)}%", True, BLANCO)
        self.pantalla.blit(texto_volumen, (ANCHO_VENTANA - 200, 70))
    
    def dibujar_pantalla_fin(self):
        """Dibuja la pantalla de fin de juego."""
        # Fondo semi-transparente
        overlay = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.pantalla.blit(overlay, (0, 0))
        
        # Texto de fin de juego
        if self.ganador == "Empate":
            texto_fin = self.fuente_grande.render("¡EMPATE!", True, AMARILLO)
        else:
            texto_fin = self.fuente_grande.render(f"¡{self.ganador} GANA!", True, AMARILLO)
        
        texto_reiniciar = self.fuente.render("Presiona R para reiniciar", True, BLANCO)
        
        # Centrar texto
        rect_fin = texto_fin.get_rect(center=(ANCHO_VENTANA//2, ALTO_VENTANA//2 - 50))
        rect_reiniciar = texto_reiniciar.get_rect(center=(ANCHO_VENTANA//2, ALTO_VENTANA//2 + 20))
        
        self.pantalla.blit(texto_fin, rect_fin)
        self.pantalla.blit(texto_reiniciar, rect_reiniciar)
    
    def ejecutar(self):
        ejecutando = True
        while ejecutando:
            ejecutando = self.manejar_eventos()
            self.actualizar()
            self.actualizar_efectos()
            self.dibujar()
            self.reloj.tick(FPS)
        
        # Detener la música al salir
        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass
                
        pygame.quit()

if __name__ == "__main__":
    juego = Juego()
    juego.ejecutar()
