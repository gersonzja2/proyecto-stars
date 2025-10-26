#  Tanks Battle 💥

Un emocionante juego de batalla de tanques para dos jugadores locales, construido con Pygame. ¡Maniobra tu tanque, esquiva el fuego enemigo y destruye a tu oponente en un campo de batalla lleno de obstáculos!

  <!-- Reemplaza con una captura de pantalla real de tu juego -->

## 🚀 Características

-   **Batallas 1v1:** Compite contra un amigo en el mismo teclado.
-   **Controles Intuitivos:** Sistema de control basado en rotación y avance, con disparo automático al moverse.
-   **Mapa Dinámico:** El campo de batalla se genera aleatoriamente en cada partida con diferentes tipos de obstáculos.
-   **Obstáculos Destructibles:** Algunos obstáculos, como los arbustos y los muros de ladrillo, pueden ser destruidos por los disparos.
-   **Música y Sonido:** Música de fondo con controles de volumen y la opción de silenciarla.
-   **Efectos Visuales:** Explosiones y parpadeo de invulnerabilidad para una experiencia más inmersiva.
-   **Sistema de Puntuación:** Gana puntos por cada vez que impactas al oponente.

## 🎮 Cómo Jugar

El objetivo es simple: ¡destruir el tanque de tu oponente! Cada tanque tiene 3 vidas. El último tanque en pie gana la partida.

### Controles

**Tanque Azul (Jugador 1):**
-   `W`: Avanzar y Disparar
-   `A`: Girar a la izquierda
-   `D`: Girar a la derecha

**Tanque Rojo (Jugador 2):**
-   `I`: Avanzar y Disparar
-   `J`: Girar a la izquierda
-   `L`: Girar a la derecha

**Controles del Juego:**
-   `P`: Pausar o reanudar el juego.
-   `R`: Reiniciar la partida.
-   `M`: Pausar o reanudar la música.
-   `+` / `-`: Subir o bajar el volumen de la música.
-   `ESC`: Salir del juego.

### Obstáculos

-   **Rocas 🪨:** Indestructibles. Bloquean tanto el movimiento como los disparos.
-   **Arbustos 🌳:** Destructibles. Se destruyen con 2 impactos.
-   **Muros de Ladrillo 🧱:** Destructibles. Son más resistentes y requieren 5 impactos para ser destruidos.
-   **Cajas de Madera 📦:** Destructibles. Resistencia media, se rompen con 3 impactos.

## 🛠️ Requisitos e Instalación

Para ejecutar este juego, necesitas tener Python y la librería Pygame instalados.

1.  **Instalar Pygame:**
    ```bash
    pip install pygame
    ```

2.  **Archivo de Música:**
    Asegúrate de tener todos los archivos de sonido y música (`.wav`, `.mp3`) dentro de una carpeta llamada `assets/sounds/` en el directorio principal del proyecto.

3.  **Ejecutar el juego:**
    ```bash
    python juego.py
    ```