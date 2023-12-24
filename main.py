import tkinter as tk
from tkinter import messagebox, filedialog

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
    pass

def delete_game():
    # Comprueba si hay un elemento seleccionado
    if listbox_partidas.curselection():
        # Obtiene el índice del elemento seleccionado
        index = listbox_partidas.curselection()[0]
        
        # Crea una conexión a la base de datos SQLite
        conn = sqlite3.connect('partidas.db')
        c = conn.cursor()

        # Obtiene el ID de la partida a eliminar
        c.execute('SELECT id FROM partidas')
        ids = c.fetchall()
        id_partida = ids[index][0]

        # Elimina la partida de la base de datos
        c.execute('DELETE FROM partidas WHERE id = ?', (id_partida,))

        # Guarda los cambios y cierra la conexión a la base de datos
        conn.commit()
        conn.close()

        # Elimina el elemento de la lista
        listbox_partidas.delete(index)

        # print("Deleted")

def update_games_list():
    # Crea una conexión a la base de datos SQLite
    conn = sqlite3.connect('partidas.db')
    c = conn.cursor()

    # Obtiene todas las partidas de la base de datos
    c.execute('SELECT pgn FROM partidas')
    partidas = c.fetchall()

    # Limpia la lista de partidas
    listbox_partidas.delete(0, tk.END)

    # Añade las partidas a la lista
    for partida in partidas:
        # Lee la partida PGN
        partida_pgn = chess.pgn.read_game(io.StringIO(partida[0]))

        # Extrae los nombres, el resultado, el ELO, la fecha y el evento de la partida
        blancas = partida_pgn.headers['White']
        negras = partida_pgn.headers['Black']
        resultado = partida_pgn.headers['Result']
        elo_blancas = partida_pgn.headers['WhiteElo']
        elo_negras = partida_pgn.headers['BlackElo']
        fecha = partida_pgn.headers['Date']
        evento = partida_pgn.headers['Event']

        # Formatea la información para mostrarla en la lista
        info_partida = f"{evento}, {fecha}, ({elo_blancas}) {blancas} {resultado} {negras} ({elo_negras})"

        listbox_partidas.insert(tk.END, info_partida)

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

def on_select(event):
    # Get selected line index
    index = listbox_partidas.curselection()[0]
    
    # Get the line's text
    text = listbox_partidas.get(index)

    # print(f"You selected item {index}: {text}")

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

# Crea una lista para mostrar las partidas
listbox_partidas = tk.Listbox(window)
listbox_partidas.pack(fill=tk.BOTH, expand=1)

# Bind the function to listbox
listbox_partidas.bind('<<ListboxSelect>>', on_select)

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