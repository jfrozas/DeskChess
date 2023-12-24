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
        item = treeview_partidas.selection()[0]
        item_data = treeview_partidas.item(item)
        text_value = item_data['text']

        # Crea una conexión a la base de datos SQLite
        conn = sqlite3.connect('partidas.db')
        c = conn.cursor()

        # Obtiene el PGN de la partida a visualizar
        c.execute('SELECT pgn FROM partidas')
        partidas = c.fetchall()
        pgn_partida = partidas[int(text_value)-1][0]

        # Lee la partida PGN
        partida = chess.pgn.read_game(io.StringIO(pgn_partida))
        blancas = partida.headers['White']
        negras = partida.headers['Black']

        # Crea una nueva ventana para mostrar la partida
        ventana_partida = tk.Toplevel(window)
        ventana_partida.title(f"{blancas} VS {negras}")

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