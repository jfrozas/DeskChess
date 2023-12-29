# DeskChess

Aplicacion para el almacenamiento y visualización de partidas de ajedrez en formato PGN.

![License](https://img.shields.io/badge/License-MIT-yellow.svg)
[![CodeFactor](https://www.codefactor.io/repository/github/jfrozas/DeskChess/badge)](https://www.codefactor.io/repository/github/jfrozas/DeskChess)
![GitHub last commit](https://img.shields.io/github/last-commit/jfrozas/DeskChess)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/jfrozas/DeskChess)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fjfrozas%2FDeskChess&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)

## Requisitos

python-chess

Pillow

tkinter

sqlite3

Normalmente tkinter y sqlite ya vienen instaladas con la distribución de python.

```bash
pip install -r requirements.txt
```

## Uso

Cuando se ejecuta el programa

```bash
python main.py
```

Se abrira una ventana de la siguiente forma:

![Ventana inicial](assets/f1.png)

En esta, se pueden ver 3 botones. Si se selecciona añadir partida, se dejará seleccionar un fichero .pgn para añadirlo a la Base de Datos. Este puede tener una o más partidas.

Si se selecciona una partida (Click izquierdo sobre esta), y se selecciona eliminar, se eliminará de la Base de Datos.

Por último, si se selecciona una partida, y se clicka en ver partida, se abrirá una nueva ventana  de la forma:

![Ventana secundaria](assets/f2.png)

En esta, se puede ver la partida, los movimientos, y movernos hacia adelante o atrás en estos, los cuales serán reflejados en el tablero.

Cuando se haga el primer movimiento, también aparecerán en la pantalla los tres mejores movimientos para esa posición, además de una puntuación aproximada de esta, dada por el módulo Stockfish.

![Ventana secundaria 2](assets/f3.png)
