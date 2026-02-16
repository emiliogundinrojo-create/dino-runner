# Modern Dinosaur Game

Versión del juego hecha **100% en Python** con **Tkinter**.

## Requisitos
- Python 3.10+
- Tkinter

## Ejecutar
```bash
python main.py
```

## Menú principal
- **Jugar**: entra en la partida
- **Tienda**: compra/equipa skins con Emilianos
- **Salir**: cierra la aplicación

## Pausa en partida
Al pulsar `R` se abre el menú de pausa:
- **Seguir jugando**: reanuda exactamente desde la misma posición y estado
- **Volver al menú**

## Cuando pierdes
Al morir aparecen 2 opciones:
- **Jugar otra partida**: reinicia puntuación, mantiene récord y Emilianos
- **Volver al menú**

## Tienda de skins
La tienda tiene fondo con división central tipo pared:
- Lado izquierdo: `Skin predeterminada` + `Dragon infernal`
- Lado derecho: `Verdoso` + `Skin Cristiano Ronaldo`

Precios:
- **Skin predeterminada** (gratis)
- **Dragon infernal** (50 Emilianos)
- **Verdoso** (20 Emilianos)
- **Skin Cristiano Ronaldo** (80 Emilianos)

## Controles (en partida)
- `Espacio` o `↑`: Saltar
- `↓`: Agacharse
- `R`: Pausar juego (abre menú de pausa)
- Click izquierdo: Saltar

## Mecánicas
- La puntuación sube **10 puntos por segundo**.
- El cielo alterna entre **día** y **noche** cada **750 puntos** (0 día, 750 noche, 1500 día...).
- Las monedas **Emilianos** vuelven a aparecer en varias alturas, con algo menos de probabilidad, y sí se desplazan para poder recogerlas.
- Los textos de branding (`Modern Dinosaur Game` y `MERCADONA`) solo aparecen cuando estás en la tienda.
- El texto de ayuda solo aparece en menú principal y partida (no en tienda).
