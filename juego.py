import pygame
import math
import random
from enum import Enum, auto
import effects
from asset_manager import AssetManager
from tank import Tanque
from obstacles import Obstaculo, Roca, Arbusto, Muro, CajaMadera
import settings as s


class GameState(Enum):
    """Enum para los estados del juego."""
    JUGANDO = auto()
    PAUSA = auto()
    FIN_PARTIDA = auto()

# Inicializar pygame
pygame.init()
        
class Bala:
    """Representa un proyectil disparado por un tanque."""
    def __init__(self, x, y, angulo, color):
        self.x = x
        self.y = y
        self.velocidad = 10
        self.angulo = angulo
        self.color = color
        self.radio = 4
        self.rect = pygame.Rect(x - self.radio, y - self.radio, self.radio * 2, self.radio * 2)
        self.tiempo_creacion = pygame.time.get_ticks() # Para controlar su vida útil.
        self.tiempo_max_vida = 3000  # 3 segundos
        
    def mover(self, dt):
        """Mueve la bala en su dirección. `dt` asegura un movimiento fluido e independiente de los FPS."""
        self.x += math.cos(self.angulo) * self.velocidad * dt * 60 # Multiplicamos por 60 para mantener la velocidad original
        self.y += math.sin(self.angulo) * self.velocidad * dt * 60
        self.rect.x = self.x - self.radio
        self.rect.y = self.y - self.radio
        
    def esta_fuera_pantalla(self):
        """Comprueba si la bala ha salido de los límites de la pantalla."""
        return (self.x < -10 or self.x > s.ANCHO_VENTANA + 10 or 
                self.y < -10 or self.y > s.ALTO_VENTANA + 10)
                
    def tiempo_agotado(self):
        """Comprueba si la bala ha existido por más tiempo del permitido."""
        return pygame.time.get_ticks() - self.tiempo_creacion >= self.tiempo_max_vida


class Juego:
    """Clase principal que orquesta todo el juego: el bucle principal, estados, eventos y lógica."""
    def __init__(self):
        """Inicializa la ventana, los recursos, los objetos del juego y el estado inicial."""
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
        
        # Agrupar tanques para facilitar la iteración
        self.tanques = [self.tanque1, self.tanque2]
        # Restaurar el volumen de la sesión anterior si es necesario
        if 'volumen_actual' in self.__dict__:
            pygame.mixer.music.set_volume(self.volumen_actual)
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
        """Genera y posiciona los obstáculos en el mapa de forma aleatoria."""
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
            x = random.randint(50, s.ANCHO_VENTANA - 90)  # Evitar bordes y zona de UI
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
        """Procesa todas las entradas del usuario (teclado, cerrar ventana)."""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    # Salir del juego con ESC
                    return False
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
            if 'pausa_in' in self.assets.sounds:
                self.assets.sounds['pausa_in'].play()
            print("Juego pausado")
        elif self.estado == GameState.PAUSA:
            self.estado = GameState.JUGANDO
            if 'pausa_out' in self.assets.sounds:
                self.assets.sounds['pausa_out'].play()
            print("Juego reanudado")
    
    def actualizar(self, dt):
        """Actualiza la lógica de todos los objetos del juego en cada frame."""
        teclas_presionadas = pygame.key.get_pressed()

        # 1. Actualizar tanques (movimiento y disparo)
        tanques_activos = [t for t in self.tanques if t.vidas > 0]
        for i, tanque in enumerate(tanques_activos):
            otros_tanques = tanques_activos[:i] + tanques_activos[i+1:]
            if tanque.mover(teclas_presionadas, self.obstaculos, otros_tanques):
                bala = tanque.disparar(Bala)
                if bala:
                    self.balas.append(bala)

        # 2. Mover balas
        for bala in self.balas[:]:
            bala.mover(dt)
            # Eliminar balas que están fuera de la pantalla o que han existido demasiado tiempo
            if bala.esta_fuera_pantalla() or bala.tiempo_agotado():
                self.balas.remove(bala)
        
        # Verificar colisiones de balas
        self.verificar_colisiones() # 3. Verificar colisiones
        
        # Actualizar efectos de invulnerabilidad
        self.actualizar_invulnerabilidad() # 4. Actualizar estado de invulnerabilidad
        
        # 5. Verificar si la partida ha terminado
        if all(t.vidas <= 0 for t in self.tanques):
            self.estado = GameState.FIN_PARTIDA
            self.ganador = "Empate"
        elif self.tanque2.vidas <= 0:
            self.estado = GameState.FIN_PARTIDA
            self.ganador = "Tanque Azul"
        elif self.tanque1.vidas <= 0:
            self.estado = GameState.FIN_PARTIDA
            self.ganador = "Tanque Rojo"
    
    def actualizar_efectos(self):
        """Actualiza todos los efectos visuales y los elimina si han terminado."""
        for efecto in self.efectos[:]:
            # Cada efecto tiene su propia lógica de actualización.
            efecto.actualizar()
            if efecto.ha_terminado():
                self.efectos.remove(efecto)

    def _manejar_colision_bala_tanque(self, bala, tanque_impactado, tanque_tirador):
        """Maneja la lógica de colisión entre una bala y un tanque."""
        if (tanque_impactado.vidas > 0 and bala.rect.colliderect(tanque_impactado.rect) and
                # La bala no debe ser del mismo color que el tanque y el tanque no debe ser invulnerable.
                bala.color != tanque_impactado.color and not tanque_impactado.invulnerable):
            
            tanque_impactado.vidas -= 1
            tanque_tirador.puntuacion += 10
            tanque_impactado.invulnerable = True
            tanque_impactado.tiempo_invulnerable = pygame.time.get_ticks()
            if 'respawn' in self.assets.sounds:
                self.assets.sounds['respawn'].play()
            
            self.crear_efecto_explosion(tanque_impactado.x + 15, tanque_impactado.y + 15)
            self.balas.remove(bala)
            return True
        return False

    def verificar_colisiones(self):
        """Verifica y maneja las colisiones de las balas con los obstáculos y los tanques."""
        for bala in self.balas[:]:
            # Colisión con obstáculos usando rectángulos
            for obstaculo in self.obstaculos[:]:
                if bala.rect.colliderect(obstaculo.rect):
                    if obstaculo.destructible:
                        if obstaculo.recibir_daño():
                            self.obstaculos.remove(obstaculo)
                            # Efecto de destrucción
                            self.crear_efecto_explosion(obstaculo.x + 20, obstaculo.y + 20)
                        else:
                            # Si el obstáculo fue dañado pero no destruido, reproducir sonido de daño
                            self.assets.sounds['dano_obstaculo'].play()
                    elif isinstance(obstaculo, Roca): # Si choca con una roca
                        self.crear_efecto_chispas(bala.x, bala.y)
                        if 'ricochet' in self.assets.sounds:
                            self.assets.sounds['ricochet'].play()
                    else: # Cualquier otro obstáculo no destructible
                            self.crear_efecto_explosion(obstaculo.x + 20, obstaculo.y + 20)
                    self.balas.remove(bala)
                    break
            
            # Si la bala fue destruida por un obstáculo, no continuar.
            if bala not in self.balas:
                continue
                
            # Colisión con tanques
            if self._manejar_colision_bala_tanque(bala, self.tanque1, self.tanque2):
                continue # La bala fue destruida, pasar a la siguiente
            if self._manejar_colision_bala_tanque(bala, self.tanque2, self.tanque1):
                continue
            
            # Colisión con tanques invulnerables (crea chispas)
            for tanque in self.tanques:
                if (tanque.vidas > 0 and bala.rect.colliderect(tanque.rect) and
                    bala.color != tanque.color and tanque.invulnerable):
                    if bala in self.balas:
                        self.balas.remove(bala)
                        self.crear_efecto_chispas(bala.x, bala.y)
                        if 'golpe' in self.assets.sounds:
                            self.assets.sounds['golpe'].play()
                        break # La bala ya no existe, salimos del bucle de tanques
            if bala not in self.balas:
                continue

    
    def actualizar_invulnerabilidad(self):
        """Actualiza el estado de invulnerabilidad de los tanques."""
        tiempo_actual = pygame.time.get_ticks()
        for tanque in self.tanques:
            if tanque.invulnerable and tiempo_actual - tanque.tiempo_invulnerable > 2000:
                tanque.invulnerable = False

    def crear_efecto_chispas(self, x, y):
        """Crea un efecto de chispas en una posición."""
        num_chispas = min(8, s.MAX_EFECTOS - len(self.efectos))
        for _ in range(num_chispas):
            angulo = random.uniform(0, 2 * math.pi)
            velocidad = random.uniform(1, 4)
            dx = math.cos(angulo) * velocidad
            dy = math.sin(angulo) * velocidad
            self.efectos.append(effects.Chispas(x, y, dx, dy))

    
    def crear_efecto_explosion(self, x, y):
        """Crea un efecto visual de explosión con partículas y ondas expansivas."""
        # Se calcula un "presupuesto" de efectos para no sobrecargar el motor y causar lag.
        espacio_disponible = s.MAX_EFECTOS - len(self.efectos)
        if espacio_disponible <= 0:
            return

        # Efecto principal de explosión
        self.efectos.append(effects.Explosion(x, y))
        # Onda expansiva
        self.efectos.append(effects.Onda(x, y))
        # Destello central
        self.efectos.append(effects.Destello(x, y))

        # Partículas de la explosión
        colores_fuego = [s.AMARILLO_FUEGO, s.NARANJA_FUEGO, s.ROJO_FUEGO]
        num_particulas = min(s.PARTICULAS_EXPLOSION, espacio_disponible - 3) # -3 por los 3 efectos principales.
        for _ in range(num_particulas):
            angulo = random.uniform(0, 2 * math.pi)
            velocidad = random.uniform(2, 5)
            dx = math.cos(angulo) * velocidad
            dy = math.sin(angulo) * velocidad
            color = random.choice(colores_fuego)
            self.efectos.append(effects.Particula(x, y, dx, dy, color))

        # Humo
        num_humo = min(3, s.MAX_EFECTOS - len(self.efectos))
        for _ in range(num_humo):
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
        
        self.tanques = [self.tanque1, self.tanque2]
        self.balas = []
        self.efectos = []
        self.obstaculos = []
        self.crear_obstaculos()
        self.estado = GameState.JUGANDO
        self.ganador = None
        # La música continúa reproduciéndose
    
    def ejecutar(self):
        """El bucle principal del juego. Se ejecuta hasta que el jugador cierra la ventana."""
        ejecutando = True
        while ejecutando:
            # Delta time para un movimiento independiente de los FPS
            dt = self.reloj.tick(s.FPS) / 1000.0

            # 1. Manejar eventos (común a todos los estados)
            ejecutando = self.manejar_eventos()

            # 2. Actualizar estado del juego (solo si se está jugando)
            if self.estado == GameState.JUGANDO:
                self.actualizar(dt)
                self.actualizar_efectos()

            # 3. Dibujar en pantalla (siempre, pero el renderizador puede cambiar según el estado)
            self.renderer.dibujar(self)
        
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
        # Obtener las fuentes cargadas por el AssetManager.
        self.fuente_grande = assets.fonts.get('grande')
        self.fuente = assets.fonts.get('normal')
        self.fuente_pequeña = assets.fonts.get('pequena')

    def dibujar(self, juego):
        """Dibuja todos los elementos del juego."""
        self.pantalla.fill(s.NEGRO)
        # El orden de dibujado es importante: fondo, obstáculos, tanques, balas, efectos, UI.
        
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

        # Actualiza la pantalla para mostrar todo lo dibujado.
        pygame.display.flip()

    def dibujar_tanque(self, tanque):
        """Dibuja un tanque, su cañón y sus indicadores de vida."""
        tiempo_actual = pygame.time.get_ticks()
        # Efecto de parpadeo cuando el tanque es invulnerable.
        if tanque.invulnerable and (tiempo_actual // 100) % 2:
            return

        # Cuerpo del tanque
        pygame.draw.rect(self.pantalla, tanque.color, (tanque.x, tanque.y, tanque.ancho, tanque.alto))
        pygame.draw.rect(self.pantalla, s.BLANCO, (tanque.x + 2, tanque.y + 2, tanque.ancho - 4, tanque.alto - 4), 2)
        
        # Cañón del tanque, apuntando en la dirección del ángulo.
        cañon_x = tanque.x + tanque.ancho // 2 + math.cos(tanque.angulo) * 20
        cañon_y = tanque.y + tanque.alto // 2 + math.sin(tanque.angulo) * 20
        pygame.draw.line(self.pantalla, tanque.color, 
                        (tanque.x + tanque.ancho // 2, tanque.y + tanque.alto // 2),
                        (cañon_x, cañon_y), 5)
        
        # Indicadores de vida sobre el tanque.
        for i in range(tanque.vidas):
            color_vida = s.ROJO
            pygame.draw.circle(self.pantalla, color_vida, 
                             (int(tanque.x + 5 + i * 8), int(tanque.y - 10)), 4)
            pygame.draw.circle(self.pantalla, s.BLANCO, 
                             (int(tanque.x + 5 + i * 8), int(tanque.y - 10)), 4, 1)

    def dibujar_bala(self, bala):
        """Dibuja una bala con un efecto de estela para dar sensación de velocidad."""
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

        # Dibuja el núcleo brillante de la bala.
        pygame.draw.circle(self.pantalla, bala.color, (int(bala.x), int(bala.y)), bala.radio)
        pygame.draw.circle(self.pantalla, s.BLANCO_BRILLANTE, (int(bala.x), int(bala.y)), bala.radio - 1)

    def dibujar_obstaculo(self, obstaculo):
        """Dibuja un obstáculo según su tipo (Roca, Arbusto, etc.)."""
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
        """Dibuja la interfaz de usuario en la parte superior de la pantalla."""
        # Fondo de la UI
        pygame.draw.rect(self.pantalla, (50, 50, 50), (0, 0, s.ANCHO_VENTANA, 80))
        pygame.draw.line(self.pantalla, s.BLANCO, (0, 80), (s.ANCHO_VENTANA, 80), 2)
        
        # Puntuaciones de los jugadores
        texto_puntuacion1 = self.fuente.render(f"Azul: {juego.tanque1.puntuacion}", True, s.AZUL) if self.fuente else None
        texto_puntuacion2 = self.fuente.render(f"Rojo: {juego.tanque2.puntuacion}", True, s.ROJO) if self.fuente else None
        self.pantalla.blit(texto_puntuacion1, (10, 10))
        self.pantalla.blit(texto_puntuacion2, (10, 40))
        
        # Instrucciones de control en el centro
        instrucciones = ["Azul: W/A/D | Rojo: I/J/L", "P=Pausa | R=Reiniciar | M=Música | +/-=Volumen | ESC=Salir"]
        if self.fuente_pequeña:
            for i, instruccion in enumerate(instrucciones):
                texto = self.fuente_pequeña.render(instruccion, True, s.AMARILLO)
                x_pos = (s.ANCHO_VENTANA - texto.get_width()) // 2
                y_pos = 15 + i * 25
                self.pantalla.blit(texto, (x_pos, y_pos))
        
        # Estado de la música y volumen a la derecha
        estado_musica = "Música: ON" if not juego.musica_pausada else "Música: OFF"
        color_musica = s.VERDE if not juego.musica_pausada else s.ROJO
        if self.fuente_pequeña:
            texto_musica = self.fuente_pequeña.render(estado_musica, True, color_musica)
            self.pantalla.blit(texto_musica, (s.ANCHO_VENTANA - 120, 10))
            
            texto_volumen = self.fuente_pequeña.render(f"Vol: {int(juego.volumen_actual * 100)}%", True, s.BLANCO)
            self.pantalla.blit(texto_volumen, (s.ANCHO_VENTANA - 120, 30))

    def dibujar_pantalla_fin(self, juego):
        """Dibuja la pantalla de fin de partida sobre el juego."""
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
    """Función principal (entry point) que crea una instancia del juego y la ejecuta."""
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