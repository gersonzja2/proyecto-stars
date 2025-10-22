#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interfaz principal del juego de tanques.
Ejecuta el juego importando la lógica desde logica.py
"""

from logica import Juego

def main():
    """Función principal que inicia el juego."""
    print("¡Bienvenido al Juego de Tanques!")
    print("Controles:")
    print("Tanque Azul: WASD para mover, ESPACIO para disparar")
    print("Tanque Rojo: IJKL para mover, ENTER para disparar")
    print("Usa el mouse para apuntar")
    print("Presiona cualquier tecla para comenzar...")
    
    try:
        juego = Juego()
        juego.ejecutar()
    except Exception as e:
        print(f"Error al ejecutar el juego: {e}")
        print("Asegúrate de tener pygame instalado: pip install pygame")

if __name__ == "__main__":
    main()
