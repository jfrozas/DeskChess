import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk

from chess import svg

import sqlite3
import chess.pgn

import io

def add_game():
    # Pide al usuario un archivo
    ruta_archivo = filedialog.askopenfilename(filetypes=[("PGN files", "*.pgn")])

    # Comprueba si el usuario seleccionó un archivo
    if ruta_archivo:
        # Crea una conexión a la base de datos SQLite
        conn = sqlite3.connect('partidas.db')
        c = conn.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS partidas (
                id INTEGER PRIMARY KEY,
                pgn TEXT
            )
        ''')

        # Abre el archivo PGN
        with open(ruta_archivo) as pgn_file:
            while True:
                # Lee una partida del archivo PGN
                partida = chess.pgn.read_game(pgn_file)

                # Si la partida es None, hemos llegado al final del archivo
                if partida is None:
                    break

                # Inserta la partida en la base de datos
                c.execute('INSERT INTO partidas (pgn) VALUES (?)', (str(partida),))

        # Guarda los cambios y cierra la conexión a la base de datos
        conn.commit()
        conn.close()

        update_games_list()



def view_game():
    if treeview_partidas.selection():
        board = chess.Board()

        item = treeview_partidas.selection()[0]
        item_data = treeview_partidas.item(item)
        text_value = item_data['text']

        # Crea una conexión a la base de datos SQLite
        conn = sqlite3.connect('partidas.db')
        c = conn.cursor()

        # Obtiene el PGN de la partida a visualizar
        c.execute('SELECT pgn FROM partidas WHERE id = ?', text_value)
        partidas = c.fetchall()

        pgn_partida = partidas[0][0]
        
        # Lee la partida PGN
        partida = chess.pgn.read_game(io.StringIO(pgn_partida))

        # Convierte los movimientos de la partida en una lista
        movimientos = list(partida.mainline_moves())
        
        # Obtiene el movimiento actual
        indice_actual = 0

        # Crea una nueva ventana para mostrar la partida
        ventana_partida = tk.Toplevel(window)
        ventana_partida.title(f"{partida.headers['White']} VS {partida.headers['Black']}")

        # Crea cuatro frames
        frame_tablero = tk.Frame(ventana_partida)
        frame_jugadas = tk.Frame(ventana_partida)
        frame_modulo = tk.Frame(ventana_partida)
        frame_vacio = tk.Frame(ventana_partida)

        # Coloca los frames en la ventana
        frame_tablero.grid(row=0, column=0, sticky='nsew')
        frame_jugadas.grid(row=0, column=1, sticky='nsew')
        frame_modulo.grid(row=1, column=0, sticky='nsew')
        frame_vacio.grid(row=1, column=1, sticky='nsew')

        # Configura las filas y columnas para que se expandan proporcionalmente
        ventana_partida.grid_rowconfigure(0, weight=1)
        ventana_partida.grid_rowconfigure(1, weight=1)
        ventana_partida.grid_columnconfigure(0, weight=1)
        ventana_partida.grid_columnconfigure(1, weight=1)

        canvas = tk.Canvas(frame_tablero, width=400, height=400)
        canvas.pack()

        # Dibuja el tablero en el Canvas
        def draw_board(board):
            # Borra todo del Canvas
            canvas.delete("all")

            # Dibuja los cuadrados del tablero
            for i in range(8):
                for j in range(8):
                    color = 'white' if (i+j)%2 == 0 else 'gray'
                    canvas.create_rectangle(i*50, j*50, (i+1)*50, (j+1)*50, fill=color)

            # Dibuja las piezas
            for i in range(8):
                for j in range(8):
                    piece = board.piece_at(chess.square(i, 7-j))
                    if piece is not None:
                        canvas.create_text(i*50+25, j*50+25, text=str(piece))

        def next_move():
            nonlocal indice_actual
            if indice_actual < len(movimientos):
                board.push(movimientos[indice_actual])
                indice_actual += 1
                draw_board(board)

        def previous_move():
            nonlocal indice_actual
            if indice_actual > 0:
                indice_actual -= 1
                board.pop()
                draw_board(board)

        # Crea un widget Scrollbar
        scrollbar = tk.Scrollbar(frame_jugadas)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(frame_jugadas, height= 20)
        listbox.pack(fill=tk.BOTH)

        # Añade las jugadas al frame
        for i in range(0, len(movimientos), 2):
            turno = i // 2 + 1
            movimiento_blancas = movimientos[i]
            if i + 1 < len(movimientos):
                movimiento_negras = movimientos[i + 1]
            else:
                movimiento_negras = ''
            jugada = f"{turno}. {movimiento_blancas} {movimiento_negras}"
            listbox.insert(tk.END, jugada)

        btn_previous_move = tk.Button(frame_tablero, text="Previous", command=previous_move)
        btn_previous_move.pack(side=tk.LEFT)

        btn_next_move = tk.Button(frame_tablero, text="Next", command=next_move)
        btn_next_move.pack(side=tk.LEFT)

        scrollbar.config(command=listbox.yview)

        draw_board(board)

        ventana_partida.mainloop()



def delete_game():
    # Comprueba si hay un elemento seleccionado
    if treeview_partidas.selection():
        # Obtiene el ítem seleccionado
        item = treeview_partidas.selection()[0]
        item_data = treeview_partidas.item(item)
        text_value = item_data['text']

        # Crea una conexión a la base de datos SQLite
        conn = sqlite3.connect('partidas.db')
        c = conn.cursor()

        id_partida = text_value

        # Elimina la partida de la base de datos
        try:
            c.execute('DELETE FROM partidas WHERE id = ?', (id_partida,))
            print(f"DELETE FROM partidas WHERE id = {id_partida}")
        except Exception as e:
            print(f"An error occurred: {e}")

        # Guarda los cambios y cierra la conexión a la base de datos
        conn.commit()
        conn.close()

        # Elimina el ítem del Treeview
        treeview_partidas.delete(item)


def update_games_list():
    # Crea una conexión a la base de datos SQLite
    conn = sqlite3.connect('partidas.db')
    c = conn.cursor()

    # Obtiene todas las partidas de la base de datos
    c.execute('SELECT id, pgn FROM partidas')
    partidas = c.fetchall()

    # Limpia la lista de partidas
    for i in treeview_partidas.get_children():
        treeview_partidas.delete(i)

    # Añade las partidas a la lista
    for partida in partidas:

        # Lee la partida PGN
        partida_pgn = chess.pgn.read_game(io.StringIO(partida[1]))

        # Extrae los nombres, el resultado, el ELO, la fecha y el evento de la partida
        blancas = partida_pgn.headers['White']
        negras = partida_pgn.headers['Black']
        resultado = partida_pgn.headers['Result']
        elo_blancas = partida_pgn.headers['WhiteElo']
        elo_negras = partida_pgn.headers['BlackElo']
        fecha = partida_pgn.headers['Date']
        evento = partida_pgn.headers['Event']

        # Inserta la información en el Treeview
        treeview_partidas.insert('', 'end', text=str(partida[0]), values=(evento, fecha, elo_blancas, blancas, resultado, negras, elo_negras))

def mostrar_partidas():
    # Crea una conexión a la base de datos SQLite
    conn = sqlite3.connect('partidas.db')
    c = conn.cursor()

    # Obtiene todas las partidas de la base de datos
    c.execute('SELECT id FROM partidas')
    ids = c.fetchall()

    # Muestra los IDs de las partidas
    for id in ids:
        print(id[0])



window = tk.Tk()
window.title("Chess App")

# Ajusta el tamaño de la ventana a 1920x1080
window.geometry("1000x800")

frame = tk.Frame(window)
frame.pack()

btn_add_game = tk.Button(frame, text="Añadir partida (PGN)", command=add_game)
btn_add_game.pack(side=tk.LEFT)

btn_view_game = tk.Button(frame, text="Ver partida", command=view_game)
btn_view_game.pack(side=tk.LEFT)

btn_delete_game = tk.Button(frame, text="Eliminar partida", command=delete_game)
btn_delete_game.pack(side=tk.LEFT)

btn_add_game = tk.Button(frame, text="Ver BD", command=mostrar_partidas)
btn_add_game.pack(side=tk.LEFT)


# Crea un widget Scrollbar
scrollbar = tk.Scrollbar(window)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

treeview_partidas = ttk.Treeview(window, yscrollcommand=scrollbar.set)

# Define las columnas
treeview_partidas['columns'] = ("Evento", "Fecha","ELO Jugador 1" ,"Jugador 1", "Resultado", "Jugador 2", "ELO Jugador 2")

# Formatea las columnas
treeview_partidas.column("#0", width=0, stretch=tk.NO)
treeview_partidas.column("Evento", anchor=tk.W, width=80)
treeview_partidas.column("Fecha", anchor=tk.W, width=40)
treeview_partidas.column("ELO Jugador 1", anchor=tk.W, width=20)
treeview_partidas.column("Jugador 1", anchor=tk.W, width=80)
treeview_partidas.column("Resultado", anchor=tk.W, width=20)
treeview_partidas.column("Jugador 2", anchor=tk.W, width=80)
treeview_partidas.column("ELO Jugador 2", anchor=tk.W, width=20)

# Crea los encabezados de las columnas
treeview_partidas.heading("#0", text="", anchor=tk.W)
treeview_partidas.heading("Evento", text="Evento", anchor=tk.W)
treeview_partidas.heading("Fecha", text="Fecha", anchor=tk.W)
treeview_partidas.heading("ELO Jugador 1", text="ELO Jugador 1", anchor=tk.W)
treeview_partidas.heading("Jugador 1", text="Jugador 1", anchor=tk.W)
treeview_partidas.heading("Resultado", text="Resultado", anchor=tk.W)
treeview_partidas.heading("Jugador 2", text="Jugador 2", anchor=tk.W)
treeview_partidas.heading("ELO Jugador 2", text="ELO Jugador 2", anchor=tk.W)

treeview_partidas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Conecta la Scrollbar al Treeview
scrollbar.config(command=treeview_partidas.yview)

def crear_tabla_partidas():
    conn = sqlite3.connect('partidas.db')
    # Crea una tabla para almacenar las partidas
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS partidas (
            id INTEGER PRIMARY KEY,
            pgn TEXT
        )
    ''')
    conn.commit()
    conn.close()


crear_tabla_partidas()

update_games_list()

window.mainloop()