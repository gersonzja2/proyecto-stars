# Juego de Tanques

Un juego de batalla de tanques para dos jugadores desarrollado en Python con Pygame.

## Características

- **Dos tanques controlables** con diferentes controles
- **Sistema de disparo** con balas que se mueven por la pantalla
- **Obstáculos destructibles** (arbustos) y no destructibles (rocas)
- **Sistema de vidas y puntuación**
- **Detección de colisiones** completa
- **Controles intuitivos** con mouse para apuntar

## Controles

### Tanque Azul (Jugador 1)
- **W, A, S, D**: Mover el tanque (arriba, izquierda, abajo, derecha)
- **ESPACIO**: Disparar
- **Mouse**: Apuntar el cañón

### Tanque Rojo (Jugador 2)
- **I, J, K, L**: Mover el tanque (arriba, izquierda, abajo, derecha)
- **ENTER**: Disparar
- **Mouse**: Apuntar el cañón

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

2. Usa los controles para mover tus tanques y disparar
3. Destruye los arbustos (obstáculos verdes) para abrir caminos
4. Evita las rocas (obstáculos grises) - no se pueden destruir ni atravesar
5. Dispara al tanque enemigo para ganar puntos
6. El juego termina cuando un tanque se queda sin vidas

## Objetos del juego

- **Tanques**: Tienen 3 vidas cada uno
- **Arbustos** (verdes): Se pueden destruir con disparos
- **Rocas** (grises): No se pueden destruir ni atravesar
- **Balas**: Se mueven en línea recta y desaparecen al chocar

## Estructura del proyecto

- `logica.py`: Contiene toda la lógica del juego (clases, física, colisiones)
- `interfaz.py`: Punto de entrada principal del juego
- `requirements.txt`: Dependencias del proyecto
- `README.md`: Este archivo con las instrucciones

¡Disfruta del juego!