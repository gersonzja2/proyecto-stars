# settings.py

# ---- CONFIGURACIÓN DE LA VENTANA Y JUEGO ----
ANCHO_VENTANA = 1000
ALTO_VENTANA = 700
FPS = 60

# ---- COLORES ----
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
MARRON_LADRILLO = (150, 75, 0)

# Colores para la caja de madera
MARRON_CAJA = (160, 110, 60)
MARRON_CAJA_OSCURO = (130, 80, 40)

# Colores para efectos visuales (explosiones, destellos)
AMARILLO_FUEGO = (255, 200, 0)
NARANJA_FUEGO = (255, 100, 0)
ROJO_FUEGO = (255, 0, 0)
AZUL_BRILLANTE = (100, 200, 255)
BLANCO_BRILLANTE = (255, 255, 220)

# Configuración de efectos
PARTICULAS_EXPLOSION = 8  # Número de partículas generadas por explosión.
PARTICULAS_PROPULSION = 4
DURACION_EXPLOSION = 30
DURACION_DESTELLO = 8
DURACION_PROPULSION = 10
DURACION_ESTELA = 15
MAX_EFECTOS = 50

# ---- CONFIGURACIÓN DEL MAPA ----
NUM_ROCAS = 20
NUM_ARBUSTOS = 25
NUM_MUROS = 15
NUM_CAJAS_MADERA = 10

# ---- RUTAS DE ARCHIVOS DE RECURSOS (ASSETS) ----
MUSIC_FILE = "assets/sounds/megalovia.mp3"
SOUND_SHOT = "assets/sounds/disparo.wav"
SOUND_EXPLOSION = "assets/sounds/explosion.wav"
SOUND_ENGINE = "assets/sounds/motor.wav"
SOUND_HIT = "assets/sounds/golpe.wav"
SOUND_RICOCHET = "assets/sounds/ricochet.wav" # Sonido para bala rebotando en roca
SOUND_OBSTACLE_HIT = "assets/sounds/dano_muro.wav" # Sonido para obstáculo dañado
SOUND_PAUSE_IN = "assets/sounds/pausa_in.wav" # Sonido al pausar
SOUND_PAUSE_OUT = "assets/sounds/pausa_out.wav" # Sonido al reanudar
SOUND_RESPAWN = "assets/sounds/respawn.wav" # Sonido para reaparición/invulnerabilidad