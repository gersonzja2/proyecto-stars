# Juego de Tanques

Un juego de batalla de tanques para dos jugadores desarrollado en Python con Pygame.

## Características

- **Dos tanques controlables** con rotación 360 grados
- **Sistema de disparo automático** al moverse
- **Obstáculos destructibles** (arbustos) y no destructibles (rocas)
- **Sistema de vidas y puntuación** con efectos visuales
- **Detección de colisiones** optimizada
- **Música de fondo** con controles de volumen
- **Generación aleatoria** de obstáculos en cada partida
- **Efectos visuales** de explosiones y daño

## Controles

### Tanque Azul (Jugador 1)
- **W**: Avanzar hacia adelante y disparar automáticamente
- **A**: Girar hacia la izquierda
- **D**: Girar hacia la derecha

### Tanque Rojo (Jugador 2)
- **I**: Avanzar hacia adelante y disparar automáticamente
- **J**: Girar hacia la izquierda
- **L**: Girar hacia la derecha

### Controles Generales
- **R**: Reiniciar partida (en cualquier momento)
- **M**: Pausar/Reanudar música
- **+/-**: Ajustar volumen de la música
- **ESC**: Salir del juego

## Instalación

1. Asegúrate de tener Python 3.6 o superior instalado
2. Instala pygame:
   ```bash
   pip install pygame
   ```

## Cómo jugar

1. Ejecuta el juego:
   ```bash
   python interfaz.py
   ```

2. Usa W/I para avanzar y disparar, A/D y J/L para girar
3. Destruye los arbustos (obstáculos verdes) para abrir caminos
4. Evita las rocas (obstáculos grises) - no se pueden destruir ni atravesar
5. Los tanques disparan automáticamente al moverse
6. Cada partida tiene obstáculos en posiciones aleatorias
7. El juego termina cuando un tanque se queda sin vidas

## Objetos del juego

- **Tanques**: Tienen 3 vidas cada uno, rotación 360 grados
- **Arbustos** (verdes): Se pueden destruir con 2 disparos, cambian de color al dañarse
- **Rocas** (grises): No se pueden destruir ni atravesar
- **Balas**: Se mueven en línea recta, tienen efectos de estela
- **Efectos**: Explosiones visuales al destruir obstáculos o golpear tanques

## Estructura del proyecto

- `logica.py`: Contiene toda la lógica del juego (clases, física, colisiones)
- `interfaz.py`: Punto de entrada principal del juego
- `requirements.txt`: Dependencias del proyecto
- `README.md`: Este archivo con las instrucciones

¡Disfruta del juego!