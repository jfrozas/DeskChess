import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

import sqlite3
import chess.pgn
import chess.engine

import os

from PIL import ImageTk, Image

from datetime import datetime

import io

def add_game():
    # Pide al usuario un archivo
    ruta_archivo = filedialog.askopenfilename(filetypes=[("PGN files", "*.pgn")])

    entero_variable = tk.IntVar()

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

            
            ventana_secundaria = tk.Toplevel(window)
            ventana_secundaria.geometry('200x100')
            ventana_secundaria.title('Metiendo PGN')
            ventana_secundaria.grid()

            
            # Crear etiqueta
            etiqueta = ttk.Label(ventana_secundaria, textvariable=entero_variable)
            etiqueta.grid(column=0, row=0, padx=10, pady=10)

            entero_variable.set(0)

            while True:
                # Lee una partida del archivo PGN
                partida = chess.pgn.read_game(pgn_file)

                # Si la partida es None, hemos llegado al final del archivo
                if partida is None:
                    break

                # Inserta la partida en la base de datos
                c.execute('INSERT INTO partidas (pgn) VALUES (?)', (str(partida),))

                entero_variable.set(entero_variable.get() + 1)

                window.update_idletasks()
                ventana_secundaria.update_idletasks()

        # Guarda los cambios y cierra la conexión a la base de datos
        conn.commit()
        conn.close()
        
        update_games_list()
        ventana_secundaria.destroy()



def view_game():
    if treeview_partidas.selection():
        board = chess.Board()

        images = {}

        item = treeview_partidas.selection()[0]
        item_data = treeview_partidas.item(item)
        text_value = item_data['text']

        # Crea una conexión a la base de datos SQLite
        conn = sqlite3.connect('partidas.db')
        c = conn.cursor()

        # Obtiene el PGN de la partida a visualizar
        c.execute('SELECT pgn FROM partidas WHERE id = ?', (text_value,))
        partidas = c.fetchall()

        pgn_partida = partidas[0][0]
        
        # Lee la partida PGN
        partida = chess.pgn.read_game(io.StringIO(pgn_partida))

        # Convierte los movimientos de la partida en una lista
        movimientos = list(partida.mainline_moves())
        
        # Obtiene el movimiento actual
        indice_actual = 0

        variable = tk.StringVar(value="No se ha hecho ningun movimiento")

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
                        if piece.color == chess.WHITE:
                            filename = os.path.join("Piezas", f"white_{str(piece)}.png")
                        else:
                            filename = os.path.join("Piezas", f"black_{str(piece)}.png")
                        image = Image.open(filename)
                        image = image.resize((50, 50), Image.ANTIALIAS)
                        photo = ImageTk.PhotoImage(image)
                        images[(i, j)] = photo
                        canvas.create_image(i*50+25, j*50+25, image=photo)

        def next_move():
            nonlocal indice_actual
            if indice_actual < len(movimientos):
                board.push(movimientos[indice_actual])
                indice_actual += 1
                variable.set(str((indice_actual-1) // 2 + 1) + " " + str(movimientos[indice_actual-1]))
                draw_board(board)

        def previous_move():
            nonlocal indice_actual
            if indice_actual > 0:
                indice_actual -= 1
                variable.set(str((indice_actual-1) // 2 + 1) + " " +  str(movimientos[indice_actual-1]))
                board.pop()
                draw_board(board)
                    
        # Crea un widget Scrollbar
        scrollbar = tk.Scrollbar(frame_jugadas)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # listbox = tk.Listbox(frame_jugadas, height= 20)
        # listbox.pack(fill=tk.BOTH)

        treeview2= ttk.Treeview(frame_jugadas, yscrollcommand=scrollbar.set)
        treeview2['columns'] = ("Turno", "Blancas", "Negras")

        # Formatea las columnas
        treeview2.column("#0", width=0, stretch=tk.NO)
        treeview2.column("Turno", anchor=tk.W, width=40)
        treeview2.column("Blancas", anchor=tk.W, width=60)
        treeview2.column("Negras", anchor=tk.W, width=60)

        # Crea los encabezados de las columnas
        treeview2.heading("#0", text="", anchor=tk.W)
        treeview2.heading("Turno", text="Turno", anchor=tk.W)
        treeview2.heading("Blancas", text="Blancas", anchor=tk.W)
        treeview2.heading("Negras", text="Negras", anchor=tk.W)

        treeview2.tag_configure("highlight", background="yellow")

        # Añade las jugadas al frame
        for i in range(0, len(movimientos), 2):
            turno = i // 2 + 1
            movimiento_blancas = movimientos[i]
            if i + 1 < len(movimientos):
                movimiento_negras = movimientos[i + 1]
            else:
                movimiento_negras = ''
            
            treeview2.insert('', 'end', text=str(turno), values=(turno, movimiento_blancas, movimiento_negras))

        def change_highlighted_row():
            # Remove highlight from current row
            for child in treeview2.get_children():
                if "highlight" in treeview2.item(child)["tags"]:
                    treeview2.item(child, tags=())
                    
            # Highlight new row
            for child in treeview2.get_children():
                if treeview2.item(child)["text"] == str(((indice_actual - 1) // 2) + 1):
                    treeview2.item(child, tags=("highlight",))

        def update_label():
            # Get the top 3 moves from Stockfish
            info = engine.analyse(board, limit=chess.engine.Limit(time=0.1), multipv=3)
            top_moves = [info[var]["pv"][0] for var in range(3)]
            top_scores = [info[var]["score"].relative.score()/100 for var in range(3)]
            # Update the label with the top moves and their scores
            text = ""
            for i, move in enumerate(top_moves):
                text += f"{i+1}. {move} ({top_scores[i]:+.2f})\n"
            label3.config(text=text)

        def prev():
            previous_move()
            change_highlighted_row()
            update_label()

        def next():
            next_move()
            change_highlighted_row()
            update_label()


        btn_previous_move = tk.Button(frame_tablero, text="Previous", command=prev)
        btn_previous_move.pack(side=tk.LEFT)

        btn_next_move = tk.Button(frame_tablero, text="Next", command=next)
        btn_next_move.pack(side=tk.LEFT)

        label2 = tk.Label(frame_tablero, textvariable="   ")
        label2.pack(side=tk.LEFT)

        label = tk.Label(frame_tablero, textvariable=variable)
        label.pack(side=tk.LEFT)

        label3 = tk.Label(frame_modulo, text="")
        label3.pack(side=tk.LEFT)


        scrollbar.config(command=treeview2.yview)

        treeview2.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

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

    conn.commit()
    conn.close()


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

def treeview_sort_column(tv, col, reverse):
    column_index = tv["columns"].index(col)
    l = [(str(tv.item(k)["values"][column_index]), k) for k in tv.get_children('')]
    l.sort(key=lambda t: t, reverse=reverse)
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)
    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))

def sort():
    treeview_sort_column(treeview_partidas, "Evento", False)

def treeview_sort_column2(tv, col, reverse):
    column_index = tv["columns"].index(col)
    l = [(datetime.strptime(str(tv.item(k)["values"][column_index]), '%Y.%m.%d'), k) for k in tv.get_children('')]
    l.sort(key=lambda t: t[0], reverse=reverse)
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)
    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))

def sort2():
    treeview_sort_column2(treeview_partidas, "Fecha", True)

engine = chess.engine.SimpleEngine.popen_uci("stockfish/stockfish-windows-x86-64-avx2.exe")

window = tk.Tk()
window.title("DeskChess")

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

# btn_add_game = tk.Button(frame, text="Ver BD", command=mostrar_partidas)
# btn_add_game.pack(side=tk.LEFT)

frame2 = tk.Frame(window)
frame2.pack()

label3 = tk.Label(frame2, text="Filtros")
label3.pack(side=tk.LEFT)

btn_add_game = tk.Button(frame2, text="Evento", command=sort)
btn_add_game.pack(side=tk.LEFT)

btn_add_game = tk.Button(frame2, text="Fecha", command=sort2)
btn_add_game.pack(side=tk.LEFT)

# Crea un widget Scrollbar
scrollbar = tk.Scrollbar(window)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

treeview_partidas = ttk.Treeview(window, yscrollcommand=scrollbar.set)

# Define las columnas
treeview_partidas['columns'] = ("Evento", "Fecha","ELO Jugador 1" ,"Jugador 1", "Resultado", "Jugador 2", "ELO Jugador 2")

# Formatea las columnas
treeview_partidas.column("#0", width=0, stretch=tk.NO)
treeview_partidas.column("Evento", anchor=tk.W, width=100)
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

# Function to close the engine and the app
def close_app():
    engine.close()
    window.destroy()

window.protocol("WM_DELETE_WINDOW", close_app)

window.mainloop()