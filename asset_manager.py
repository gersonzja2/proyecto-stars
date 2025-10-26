import pygame
import settings as s

class AssetManager:
    """Clase para cargar y gestionar todos los recursos del juego (sonidos, fuentes, etc.)."""
    
    def __init__(self):
        """Inicializa el gestor de assets, preparando diccionarios para sonidos y fuentes."""
        self.sounds = {}
        self.fonts = {}
        self.music_file = s.MUSIC_FILE  # Ruta al archivo de música de fondo.
        self.load_all()

    def load_all(self):
        """Carga todos los recursos necesarios para el juego."""
        self._load_sounds_and_music()
        self._load_fonts()
        print("Todos los assets han sido cargados.")

    def _load_sounds_and_music(self):
        """Inicializa el mixer, carga los efectos de sonido y la música."""
        try:
            # Inicializar el mixer de pygame
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            
            # Cargar efectos de sonido
            self.sounds = {
                'disparo': pygame.mixer.Sound(s.SOUND_SHOT),
                'explosion': pygame.mixer.Sound(s.SOUND_EXPLOSION),
                'motor': pygame.mixer.Sound(s.SOUND_ENGINE),
                'golpe': pygame.mixer.Sound(s.SOUND_HIT),
                'ricochet': pygame.mixer.Sound(s.SOUND_RICOCHET),
                'dano_obstaculo': pygame.mixer.Sound(s.SOUND_OBSTACLE_HIT),
                'pausa_in': pygame.mixer.Sound(s.SOUND_PAUSE_IN),
                'pausa_out': pygame.mixer.Sound(s.SOUND_PAUSE_OUT),
                'respawn': pygame.mixer.Sound(s.SOUND_RESPAWN)
            }
            # Ajustar volumen de los efectos
            for sound in self.sounds.values():
                sound.set_volume(0.4)
            
            # Cargar y reproducir la música de fondo en un bucle infinito (-1).
            pygame.mixer.music.load(self.music_file)
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)
            
            print("Música y efectos de sonido cargados correctamente.")
        except (pygame.error, FileNotFoundError) as e:
            # Si hay un error (ej. no se encuentran los archivos), se informa en consola.
            print(f"Error al cargar audio: {e}. El juego continuará sin sonido.")
            # Se desactiva el mixer para evitar errores posteriores.
            pygame.mixer.quit()
            self.sounds = {}

    def _load_fonts(self):
        """Carga todas las fuentes utilizadas en el juego."""
        try:
            # Carga fuentes de diferentes tamaños para la interfaz de usuario.
            self.fonts = {
                'grande': pygame.font.Font(None, 48),
                'normal': pygame.font.Font(None, 36),
                'pequena': pygame.font.Font(None, 24)
            }
            print("Fuentes cargadas correctamente.")
        except pygame.error as e:
            # Si las fuentes personalizadas fallan, Pygame usará su fuente por defecto.
            print(f"No se pudieron cargar las fuentes: {e}. Usando fuentes por defecto.")
            self.fonts = {
                'grande': pygame.font.Font(None, 48),
                'normal': pygame.font.Font(None, 36),
                'pequena': pygame.font.Font(None, 24)
            }