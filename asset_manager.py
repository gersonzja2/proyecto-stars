import pygame
import settings as s

class AssetManager:
    """Clase para cargar y gestionar todos los recursos del juego (sonidos, fuentes, etc.)."""
    def __init__(self):
        self.sounds = {}
        self.fonts = {}
        self.music_file = s.MUSIC_FILE
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
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            
            # Cargar efectos de sonido
            self.sounds = {
                'disparo': pygame.mixer.Sound(s.SOUND_SHOT),
                'explosion': pygame.mixer.Sound(s.SOUND_EXPLOSION),
                'motor': pygame.mixer.Sound(s.SOUND_ENGINE),
                'golpe': pygame.mixer.Sound(s.SOUND_HIT)
            }
            # Ajustar volumen de los efectos
            for sound in self.sounds.values():
                sound.set_volume(0.4)
            
            # Cargar y reproducir la música de fondo
            pygame.mixer.music.load(self.music_file)
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)
            
            print("Música y efectos de sonido cargados correctamente.")
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error al cargar audio: {e}. El juego continuará sin sonido.")
            # Asegurarse de que el mixer no cause problemas si falló
            pygame.mixer.quit()
            self.sounds = {}

    def _load_fonts(self):
        """Carga todas las fuentes utilizadas en el juego."""
        try:
            self.fonts = {
                'grande': pygame.font.Font(None, 48),
                'normal': pygame.font.Font(None, 36),
                'pequena': pygame.font.Font(None, 24)
            }
            print("Fuentes cargadas correctamente.")
        except pygame.error as e:
            print(f"No se pudieron cargar las fuentes: {e}. Usando fuentes por defecto.")
            # En caso de error, Pygame suele tener una fuente por defecto, pero es bueno saberlo.
            self.fonts = {
                'grande': pygame.font.Font(None, 48),
                'normal': pygame.font.Font(None, 36),
                'pequena': pygame.font.Font(None, 24)
            }