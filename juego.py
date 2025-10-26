import pygame
import math
import random
import time
from enum import Enum, auto
import effects
from asset_manager import AssetManager
import settings as s


class GameState(Enum):
    """Enum para los estados del juego."""
    JUGANDO = auto()
    PAUSA = auto()
    FIN_PARTIDA = auto()

# Inicializar pygame
pygame.init()

class Tanque:
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
            
        
    def disparar(self):
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.ultimo_disparo >= self.velocidad_disparo:
            # Calcular posición de salida del cañón
            cañon_x = self.x + self.ancho // 2 + math.cos(self.angulo) * 25
            cañon_y = self.y + self.alto // 2 + math.sin(self.angulo) * 25
            
            self.ultimo_disparo = tiempo_actual
            # Reproducir sonido de disparo si está disponible
            if 'disparo' in self.juego.assets.sounds:
                self.juego.assets.sounds['disparo'].play()
            return Bala(cañon_x, cañon_y, self.angulo, self.color)
        return None
        
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
        return (self.x < -10 or self.x > s.ANCHO_VENTANA + 10 or 
                self.y < -10 or self.y > s.ALTO_VENTANA + 10)
                
    def tiempo_agotado(self):
        return self.tiempo_vida >= self.tiempo_max_vida


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


class Juego:
    def __init__(self):
        self.pantalla = pygame.display.set_mode((s.ANCHO_VENTANA, s.ALTO_VENTANA))
        pygame.display.set_caption("Juego de Tanques - Optimizado")
        self.reloj = pygame.time.Clock()

        # Cargar todos los recursos a través del AssetManager
        self.assets = AssetManager()
        self.renderer = GameRenderer(self.pantalla, self.assets)
        
        # Crear tanques
        self.tanque1 = Tanque(100, 100, s.AZUL, {
            'avanzar': pygame.K_w,
            'izquierda': pygame.K_a,
            'derecha': pygame.K_d
        }, self)
        
        self.tanque2 = Tanque(800, 500, s.ROJO, {
            'avanzar': pygame.K_i,
            'izquierda': pygame.K_j,
            'derecha': pygame.K_l
        }, self)
        
        # Listas de objetos del juego
        self.balas = []
        self.obstaculos = []
        self.efectos = []  # Para efectos visuales
        
        # Crear obstáculos
        self.crear_obstaculos()
        
        # Estado del juego
        self.estado = GameState.JUGANDO
        self.ganador = None
        self.musica_pausada = False
        self.volumen_actual = 0.3
        
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
        # Limpiar obstáculos existentes
        self.obstaculos = []
        
        # Definir áreas seguras para los tanques
        margen_tanque = 60
        area_segura_tanque1 = self.tanque1.rect.inflate(margen_tanque * 2, margen_tanque * 2)
        area_segura_tanque2 = self.tanque2.rect.inflate(margen_tanque * 2, margen_tanque * 2)
        areas_prohibidas = [area_segura_tanque1, area_segura_tanque2]

        # Crear rocas (no destructibles) - posiciones aleatorias
        for _ in range(s.NUM_ROCAS):
            x, y = self.generar_posicion_segura(areas_prohibidas)
            self.obstaculos.append(Roca(x, y))
            areas_prohibidas.append(self.obstaculos[-1].rect)
            
        # Crear arbustos (destructibles) - posiciones aleatorias
        for _ in range(s.NUM_ARBUSTOS):
            x, y = self.generar_posicion_segura(areas_prohibidas)
            self.obstaculos.append(Arbusto(x, y))
            areas_prohibidas.append(self.obstaculos[-1].rect)

        # Crear muros (destructibles y más resistentes)
        for _ in range(s.NUM_MUROS):
            x, y = self.generar_posicion_segura(areas_prohibidas)
            self.obstaculos.append(Muro(x, y))
            areas_prohibidas.append(self.obstaculos[-1].rect)
        
        # Crear cajas de madera (destructibles)
        for _ in range(s.NUM_CAJAS_MADERA):
            x, y = self.generar_posicion_segura(areas_prohibidas)
            self.obstaculos.append(CajaMadera(x, y))
            areas_prohibidas.append(self.obstaculos[-1].rect)
    
    def generar_posicion_segura(self, rects_existentes):
        """Genera una posición aleatoria que no colisione con una lista de rectángulos existentes."""
        max_intentos = 100  # Límite de intentos para evitar bucle infinito
        
        for intento in range(max_intentos):
            x = random.randint(50, s.ANCHO_VENTANA - 90)  # Evitar bordes
            y = random.randint(130, s.ALTO_VENTANA - 90)  # Evitar zona de interfaz y bordes
            
            # Crear rectángulo temporal para verificar colisiones
            nuevo_rect = pygame.Rect(x, y, 40, 40)
            
            # Verificar si colisiona con alguno de los rectángulos existentes
            if not any(nuevo_rect.colliderect(rect) for rect in rects_existentes):
                return x, y
        
        # Si no se encuentra una posición segura después de muchos intentos,
        # devolver una posición aleatoria (caso extremo)
        x = random.randint(50, s.ANCHO_VENTANA - 90)
        y = random.randint(130, s.ALTO_VENTANA - 90)
        print("Advertencia: No se pudo encontrar una posición segura. Colocando obstáculo en una posición aleatoria.")
        return x, y
    
    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    # Salir del juego con ESC
                    return False
                # Los disparos ahora son automáticos al moverse
                elif evento.key == pygame.K_r:
                    # Reiniciar juego (funciona en cualquier momento)
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
                elif evento.key == pygame.K_p:
                    # Pausar/reanudar el juego
                    self.pausar_juego()
        return True
    def pausar_juego(self):
        """Pausa o reanuda el juego."""
        if self.estado == GameState.JUGANDO:
            self.estado = GameState.PAUSA
            print("Juego pausado")
        elif self.estado == GameState.PAUSA:
            self.estado = GameState.JUGANDO
            print("Juego reanudado")
    
    def actualizar(self):
        teclas_presionadas = pygame.key.get_pressed()
        
        # Mover tanques con detección de colisiones entre ellos
        otros_tanques = [self.tanque2] if self.tanque1.vidas > 0 else []
        if self.tanque1.vidas > 0:
            debe_disparar1 = self.tanque1.mover(teclas_presionadas, self.obstaculos, otros_tanques)
            if debe_disparar1:
                bala = self.tanque1.disparar()
                if bala:
                    self.balas.append(bala)
        
        otros_tanques = [self.tanque1] if self.tanque2.vidas > 0 else []
        if self.tanque2.vidas > 0:
            debe_disparar2 = self.tanque2.mover(teclas_presionadas, self.obstaculos, otros_tanques)
            if debe_disparar2:
                bala = self.tanque2.disparar()
                if bala:
                    self.balas.append(bala)
        
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
            self.estado = GameState.FIN_PARTIDA
            self.ganador = "Empate"
        elif self.tanque1.vidas <= 0:
            self.estado = GameState.FIN_PARTIDA
            self.ganador = "Tanque Rojo"
        elif self.tanque2.vidas <= 0:
            self.estado = GameState.FIN_PARTIDA
            self.ganador = "Tanque Azul"
    
    def actualizar_efectos(self):
        """Actualiza todos los efectos visuales y los elimina si han terminado."""
        for efecto in self.efectos[:]:
            efecto.actualizar()
            if efecto.ha_terminado():
                self.efectos.remove(efecto)

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
        """Crea un efecto visual de explosión con partículas y ondas expansivas."""
        # Verificar límite de efectos
        if len(self.efectos) >= s.MAX_EFECTOS:
            # Eliminar los efectos más antiguos si se supera el límite
            self.efectos = self.efectos[-s.MAX_EFECTOS//2:]
            
        # Efecto principal de explosión
        self.efectos.append(effects.Explosion(x, y))
        
        # Onda expansiva
        self.efectos.append(effects.Onda(x, y))
        
        # Destello central (solo si no hay muchos efectos)
        if len(self.efectos) < s.MAX_EFECTOS - 10:
            self.efectos.append(effects.Destello(x, y))
        
        # Partículas de la explosión
        colores_fuego = [s.AMARILLO_FUEGO, s.NARANJA_FUEGO, s.ROJO_FUEGO]
        num_particulas = min(s.PARTICULAS_EXPLOSION, (s.MAX_EFECTOS - len(self.efectos)) // 2)
        for _ in range(num_particulas):
            angulo = random.uniform(0, 2 * math.pi)
            velocidad = random.uniform(2, 5)
            dx = math.cos(angulo) * velocidad
            dy = math.sin(angulo) * velocidad
            color = random.choice(colores_fuego)
            self.efectos.append(effects.Particula(x, y, dx, dy, color))
            
        # Humo (reducido y solo si hay espacio)
        if len(self.efectos) < s.MAX_EFECTOS - 5:
            for _ in range(min(3, (s.MAX_EFECTOS - len(self.efectos)))):
                angulo = random.uniform(0, 2 * math.pi)
                velocidad = random.uniform(1, 2)
                dx = math.cos(angulo) * velocidad
                dy = math.sin(angulo) * velocidad - 0.3
                self.efectos.append(effects.Humo(x, y, dx, dy))
        
        # Reproducir sonido de explosión
        if 'explosion' in self.assets.sounds:
            self.assets.sounds['explosion'].play()
    
    def reiniciar_juego(self):
        """Reinicia el juego a su estado inicial."""
        self.tanque1 = Tanque(100, 100, s.AZUL, {
            'avanzar': pygame.K_w,
            'izquierda': pygame.K_a,
            'derecha': pygame.K_d
        }, self)
        
        self.tanque2 = Tanque(800, 500, s.ROJO, {
            'avanzar': pygame.K_i,
            'izquierda': pygame.K_j,
            'derecha': pygame.K_l
        }, self)
        
        self.balas = []
        self.efectos = []
        self.obstaculos = []
        self.crear_obstaculos()
        self.estado = GameState.JUGANDO
        self.ganador = None
        # La música continúa reproduciéndose
    
    def ejecutar(self):
        ejecutando = True
        while ejecutando:
            # 1. Manejar eventos (común a todos los estados)
            ejecutando = self.manejar_eventos()

            # 2. Actualizar estado del juego (solo si se está jugando)
            if self.estado == GameState.JUGANDO:
                self.actualizar()
                self.actualizar_efectos()

            # 3. Dibujar en pantalla (siempre, pero el renderizador puede cambiar según el estado)
            self.renderer.dibujar(self)

            # 4. Controlar FPS
            self.reloj.tick(s.FPS)
        
        # Detener la música al salir
        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass
                
        pygame.quit()

class GameRenderer:
    """Clase responsable de todo el dibujado del juego (La Vista)."""
    def __init__(self, pantalla, assets):
        self.pantalla = pantalla
        # Obtener las fuentes del AssetManager
        self.fuente_grande = assets.fonts.get('grande')
        self.fuente = assets.fonts.get('normal')
        self.fuente_pequeña = assets.fonts.get('pequena')

    def dibujar(self, juego):
        """Dibuja todos los elementos del juego."""
        self.pantalla.fill(s.NEGRO)
        
        for obstaculo in juego.obstaculos:
            self.dibujar_obstaculo(obstaculo)
        
        if juego.tanque1.vidas > 0:
            self.dibujar_tanque(juego.tanque1)
        if juego.tanque2.vidas > 0:
            self.dibujar_tanque(juego.tanque2)
        
        for bala in juego.balas:
            self.dibujar_bala(bala)
        
        self.dibujar_efectos(juego.efectos)
        self.dibujar_ui(juego)
        
        # Dibujar overlays según el estado del juego
        if juego.estado == GameState.FIN_PARTIDA:
            self.dibujar_pantalla_fin(juego)
        elif juego.estado == GameState.PAUSA:
            self.dibujar_pantalla_pausa()

        
        pygame.display.flip()

    def dibujar_tanque(self, tanque):
        tiempo_actual = pygame.time.get_ticks()
        if tanque.invulnerable and (tiempo_actual // 100) % 2:
            return

        pygame.draw.rect(self.pantalla, tanque.color, (tanque.x, tanque.y, tanque.ancho, tanque.alto))
        pygame.draw.rect(self.pantalla, s.BLANCO, (tanque.x + 2, tanque.y + 2, tanque.ancho - 4, tanque.alto - 4), 2)
        
        cañon_x = tanque.x + tanque.ancho // 2 + math.cos(tanque.angulo) * 20
        cañon_y = tanque.y + tanque.alto // 2 + math.sin(tanque.angulo) * 20
        pygame.draw.line(self.pantalla, tanque.color, 
                        (tanque.x + tanque.ancho // 2, tanque.y + tanque.alto // 2),
                        (cañon_x, cañon_y), 5)
        
        for i in range(tanque.vidas):
            color_vida = s.ROJO
            pygame.draw.circle(self.pantalla, color_vida, 
                             (int(tanque.x + 5 + i * 8), int(tanque.y - 10)), 4)
            pygame.draw.circle(self.pantalla, s.BLANCO, 
                             (int(tanque.x + 5 + i * 8), int(tanque.y - 10)), 4, 1)

    def dibujar_bala(self, bala):
        num_estelas = 4
        for i in range(num_estelas):
            distancia = i * 3
            alpha = int(150 * (1 - i/num_estelas))
            pos_x = int(bala.x - math.cos(bala.angulo) * distancia)
            pos_y = int(bala.y - math.sin(bala.angulo) * distancia)
            radio_estela = max(1, bala.radio - i)
            
            surf = pygame.Surface((radio_estela*2, radio_estela*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*bala.color[:3], alpha), (radio_estela, radio_estela), radio_estela)
            self.pantalla.blit(surf, (pos_x - radio_estela, pos_y - radio_estela))

        pygame.draw.circle(self.pantalla, bala.color, (int(bala.x), int(bala.y)), bala.radio)
        pygame.draw.circle(self.pantalla, s.BLANCO_BRILLANTE, (int(bala.x), int(bala.y)), bala.radio - 1)

    def dibujar_obstaculo(self, obstaculo):
        if isinstance(obstaculo, Arbusto):
            pygame.draw.rect(self.pantalla, s.MARRON, (obstaculo.x + 15, obstaculo.y + 30, 10, 10))
            color_verde = s.VERDE_OSCURO if obstaculo.salud == obstaculo.salud_max else s.VERDE_CLARO
            pygame.draw.circle(self.pantalla, color_verde, (obstaculo.x + 8, obstaculo.y + 8), 12)
            pygame.draw.circle(self.pantalla, color_verde, (obstaculo.x + 32, obstaculo.y + 12), 14)
            pygame.draw.circle(self.pantalla, color_verde, (obstaculo.x + 20, obstaculo.y + 25), 10)
            pygame.draw.circle(self.pantalla, color_verde, (obstaculo.x + 12, obstaculo.y + 20), 8)
            pygame.draw.circle(self.pantalla, color_verde, (obstaculo.x + 28, obstaculo.y + 28), 9)
            if obstaculo.salud < obstaculo.salud_max:
                pygame.draw.circle(self.pantalla, s.ROJO, (obstaculo.x + 20, obstaculo.y + 20), 3)
        elif isinstance(obstaculo, Roca):
            pygame.draw.rect(self.pantalla, s.GRIS, obstaculo.rect)
            pygame.draw.rect(self.pantalla, s.GRIS_CLARO, (obstaculo.x + 2, obstaculo.y + 2, obstaculo.ancho - 4, obstaculo.alto - 4))
            pygame.draw.polygon(self.pantalla, (80, 80, 80), 
                              [(obstaculo.x + 5, obstaculo.y + 35), (obstaculo.x + 15, obstaculo.y + 5),
                               (obstaculo.x + 35, obstaculo.y + 10), (obstaculo.x + 30, obstaculo.y + 35)])
            pygame.draw.polygon(self.pantalla, (60, 60, 60), 
                              [(obstaculo.x + 10, obstaculo.y + 30), (obstaculo.x + 20, obstaculo.y + 15),
                               (obstaculo.x + 30, obstaculo.y + 20), (obstaculo.x + 25, obstaculo.y + 32)])
            pygame.draw.line(self.pantalla, (40, 40, 40), (obstaculo.x, obstaculo.y + 35), (obstaculo.x + 40, obstaculo.y + 35), 2)
        elif isinstance(obstaculo, Muro):
            pygame.draw.rect(self.pantalla, s.MARRON_LADRILLO, obstaculo.rect)
            for fila in range(4):
                for col in range(4):
                    color_ladrillo = (139, 69, 19) if (fila + col) % 2 == 0 else (160, 82, 45)
                    ladrillo_rect = pygame.Rect(obstaculo.x + col * 10, obstaculo.y + fila * 10, 10, 10)
                    pygame.draw.rect(self.pantalla, color_ladrillo, ladrillo_rect)
                    pygame.draw.rect(self.pantalla, (50, 50, 50), ladrillo_rect, 1)
        elif isinstance(obstaculo, CajaMadera):
            # Dibujar caja de madera
            pygame.draw.rect(self.pantalla, s.MARRON_CAJA, obstaculo.rect)
            pygame.draw.rect(self.pantalla, s.MARRON_CAJA_OSCURO, obstaculo.rect, 3)
            # Líneas para simular tablas
            pygame.draw.line(self.pantalla, s.MARRON_CAJA_OSCURO, (obstaculo.x, obstaculo.y + 20), (obstaculo.x + 40, obstaculo.y + 20), 2)
            pygame.draw.line(self.pantalla, s.MARRON_CAJA_OSCURO, (obstaculo.x + 20, obstaculo.y), (obstaculo.x + 20, obstaculo.y + 40), 2)

    def dibujar_efectos(self, efectos):
        """Dibuja todos los efectos visuales llamando a su propio método de dibujado."""
        for efecto in efectos:
            efecto.dibujar(self.pantalla)

    def dibujar_ui(self, juego):
        pygame.draw.rect(self.pantalla, (50, 50, 50), (0, 0, s.ANCHO_VENTANA, 80))
        pygame.draw.line(self.pantalla, s.BLANCO, (0, 80), (s.ANCHO_VENTANA, 80), 2)
        
        texto_puntuacion1 = self.fuente.render(f"Azul: {juego.tanque1.puntuacion}", True, s.AZUL) if self.fuente else None
        texto_puntuacion2 = self.fuente.render(f"Rojo: {juego.tanque2.puntuacion}", True, s.ROJO) if self.fuente else None
        self.pantalla.blit(texto_puntuacion1, (10, 10))
        self.pantalla.blit(texto_puntuacion2, (10, 40))
        
        instrucciones = ["Azul: W/A/D | Rojo: I/J/L", "P=Pausa | R=Reiniciar | M=Música | +/-=Volumen | ESC=Salir"]
        if self.fuente_pequeña:
            for i, instruccion in enumerate(instrucciones):
                texto = self.fuente_pequeña.render(instruccion, True, s.AMARILLO)
                x_pos = (s.ANCHO_VENTANA - texto.get_width()) // 2
                y_pos = 15 + i * 25
                self.pantalla.blit(texto, (x_pos, y_pos))
        
        estado_musica = "Música: ON" if not juego.musica_pausada else "Música: OFF"
        color_musica = s.VERDE if not juego.musica_pausada else s.ROJO
        if self.fuente_pequeña:
            texto_musica = self.fuente_pequeña.render(estado_musica, True, color_musica)
            self.pantalla.blit(texto_musica, (s.ANCHO_VENTANA - 120, 10))
            
            texto_volumen = self.fuente_pequeña.render(f"Vol: {int(juego.volumen_actual * 100)}%", True, s.BLANCO)
            self.pantalla.blit(texto_volumen, (s.ANCHO_VENTANA - 120, 30))

    def dibujar_pantalla_fin(self, juego):
        overlay = pygame.Surface((s.ANCHO_VENTANA, s.ALTO_VENTANA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.pantalla.blit(overlay, (0, 0))
        
        if juego.ganador == "Empate":
            texto_fin = self.fuente_grande.render("¡EMPATE!", True, s.AMARILLO) if self.fuente_grande else None
        else:
            texto_fin = self.fuente_grande.render(f"¡{juego.ganador} GANA!", True, s.AMARILLO) if self.fuente_grande else None
        
        texto_reiniciar = self.fuente.render("Presiona R para reiniciar", True, s.BLANCO) if self.fuente else None
        
        if texto_fin and texto_reiniciar:
            rect_fin = texto_fin.get_rect(center=(s.ANCHO_VENTANA//2, s.ALTO_VENTANA//2 - 50))
            rect_reiniciar = texto_reiniciar.get_rect(center=(s.ANCHO_VENTANA//2, s.ALTO_VENTANA//2 + 20))
            
            self.pantalla.blit(texto_fin, rect_fin)
            self.pantalla.blit(texto_reiniciar, rect_reiniciar)

    def dibujar_pantalla_pausa(self):
        """Dibuja la pantalla de pausa."""
        overlay = pygame.Surface((s.ANCHO_VENTANA, s.ALTO_VENTANA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.pantalla.blit(overlay, (0, 0))

        if self.fuente_grande:
            texto_pausa = self.fuente_grande.render("PAUSA", True, s.AMARILLO)
            rect_pausa = texto_pausa.get_rect(center=(s.ANCHO_VENTANA // 2, s.ALTO_VENTANA // 2))
            self.pantalla.blit(texto_pausa, rect_pausa)

def main():
    """Función principal que inicia el juego."""
    print("¡Bienvenido al Juego de Tanques!")
    print("Controles:")
    print("Tanque Azul: W=Avanzar/Disparar, A/D=Girar")
    print("Tanque Rojo: I=Avanzar/Disparar, J/L=Girar")
    print("P=Pausa | R=Reiniciar | M=Música | +/-=Volumen | ESC=Salir")
    
    try:
        juego = Juego()
        juego.ejecutar()
    except Exception as e:
        print(f"Error al ejecutar el juego: {e}")
        print("Asegúrate de tener pygame instalado: pip install pygame")

if __name__ == "__main__":
    main()