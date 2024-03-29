import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import sqlite3
import chess.pgn
import chess.engine
import matplotlib.pyplot as plt
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,  NavigationToolbar2Tk
import matplotlib.dates as mdates

import sys
sys.path.append('../DeskChess')

from PIL import ImageTk, Image
from datetime import datetime

class ChessApp:
    
    '''
    PGN Visualizer APP. Developed using Pillow, python-chess, matplolib, tkinter and sqlite3.
    '''

    def __init__(self, root):

        """
        Initializes the app

        Args: 
            self: 
            root ( tk.Tk() ): Window created with tkinter to contain the aplication

        """

        self.engine = None
        self.ico_path = None
        self.images = {}

        self.sort_reverse = {}

        self.root = root
        self.root.title("DeskChess")
        self.root.geometry("1000x800")
        self.root.minsize(500, 450)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text='Visualizador PGN')

        self.top_frame = tk.Frame(self.tab1)
        self.top_frame.pack(side=tk.TOP)

        self.button_add_game = tk.Button(self.top_frame, text="Añadir partida (PGN)", command=self.add_game)
        self.button_add_game.pack(side=tk.LEFT)

        self.btn_view_game = tk.Button(self.top_frame, text="Ver partida", command=self.view_game)
        self.btn_view_game.pack(side=tk.LEFT)

        self.btn_delete_game = tk.Button(self.top_frame, text="Eliminar partida", command=self.delete_game)
        self.btn_delete_game.pack(side=tk.LEFT)

        self.scrollbar = tk.Scrollbar(self.tab1)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.treeview_partidas = ttk.Treeview(self.tab1, yscrollcommand=self.scrollbar.set)
        self.treeview_partidas['columns'] = ("Evento", "Fecha","ELO Jugador 1" ,"Jugador 1", "Resultado", "Jugador 2", "ELO Jugador 2")

        self.treeview_partidas.column("#0", width=0, stretch=tk.NO)
        self.treeview_partidas.column("Evento", anchor=tk.W, width=100)
        self.treeview_partidas.column("Fecha", anchor=tk.W, width=40)
        self.treeview_partidas.column("ELO Jugador 1", anchor=tk.W, width=20)
        self.treeview_partidas.column("Jugador 1", anchor=tk.W, width=80)
        self.treeview_partidas.column("Resultado", anchor=tk.W, width=20)
        self.treeview_partidas.column("Jugador 2", anchor=tk.W, width=80)
        self.treeview_partidas.column("ELO Jugador 2", anchor=tk.W, width=20)

        self.treeview_partidas.heading("#0", text="", anchor=tk.W)
        self.treeview_partidas.heading("Evento", text="Evento", anchor=tk.W, command=lambda: self.sorter('1', self.treeview_partidas))
        self.treeview_partidas.heading("Fecha", text="Fecha", anchor=tk.W, command=lambda: self.sorter('2', self.treeview_partidas))
        self.treeview_partidas.heading("ELO Jugador 1", text="ELO Jugador 1", anchor=tk.W, command=lambda: self.sorter('3', self.treeview_partidas))
        self.treeview_partidas.heading("Jugador 1", text="Jugador 1", anchor=tk.W, command=lambda: self.sorter('4', self.treeview_partidas))
        self.treeview_partidas.heading("Resultado", text="Resultado", anchor=tk.W, command=lambda: self.sorter('5', self.treeview_partidas))
        self.treeview_partidas.heading("Jugador 2", text="Jugador 2", anchor=tk.W, command=lambda: self.sorter('6', self.treeview_partidas))
        self.treeview_partidas.heading("ELO Jugador 2", text="ELO Jugador 2", anchor=tk.W, command=lambda: self.sorter('7', self.treeview_partidas))

        self.treeview_partidas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.scrollbar.config(command=self.treeview_partidas.yview)

        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text='Estadísticas de Jugadores')

        self.top_frame2 = tk.Frame(self.tab2)
        self.top_frame2.pack(side=tk.TOP)

        self.button_player_stats = tk.Button(self.top_frame2, text="Generar estadisticas del jugador seleccionado", command=self.generate_player_stats)
        self.button_player_stats.pack(side=tk.LEFT)
        
        self.scrollbarp = tk.Scrollbar(self.tab2)
        self.scrollbarp.pack(side=tk.RIGHT, fill=tk.Y)

        self.treeview_players = ttk.Treeview(self.tab2, yscrollcommand=self.scrollbarp.set)
        self.treeview_players['columns'] = ("Player", "Total Games")

        self.treeview_players.column("#0", width=0, stretch=tk.NO)
        self.treeview_players.column("Player", anchor=tk.W, width=100)
        self.treeview_players.column("Total Games", anchor=tk.W, width=100)

        self.treeview_players.heading("#0", text="", anchor=tk.W)
        self.treeview_players.heading("Player", text="Player", anchor=tk.W, command=lambda: self.sorter('1', self.treeview_players))
        self.treeview_players.heading("Total Games", text="Total Games", anchor=tk.W, command=lambda: self.sorter('2', self.treeview_players))

        self.treeview_players.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.scrollbarp.config(command=self.treeview_players.yview)

        self.script_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

        self.set_icon()
        self.create_initial_db()
        self.update_treeview()
        self.add_players()

    def add_players(self):

        """
        Adds players to the treeview_players to be displayed in the second tab

        Args:
            self:

        """
        
        conn = sqlite3.connect('bd.db')
        c = conn.cursor()

        for i in self.treeview_players.get_children():
            self.treeview_players.delete(i)

        c.execute('''
        SELECT player_name
        FROM (
            SELECT player1 AS player_name FROM bd
            UNION
            SELECT player2 AS player_name FROM bd
        ) AS all_players
        WHERE player_name IS NOT NULL
        GROUP BY player_name;
        ''')

        unique_players = c.fetchall()

        for player in unique_players:

            player_name = player[0]
            c.execute('''
                SELECT COUNT(*) AS total_games
                FROM bd
                WHERE player1 = ? OR player2 = ?;
            ''', (player_name, player_name))

            total_games = c.fetchone()[0]

            self.treeview_players.insert('', 'end', text='', values=(player[0], total_games))

        conn.commit()
        conn.close()

    def generate_player_stats(self):
        """
        For one player in treeview_players, fetches its stats and generates the according graphs, creating a new window.

        Args: 
            self:

        """

        if self.treeview_players.selection():

            item = self.treeview_players.selection()[0]
            item_data = self.treeview_players.item(item)
            name = item_data['values'][0]
            totalgames = item_data['values'][1]

            conn = sqlite3.connect('bd.db')
            c = conn.cursor()

            # Wins, Losses, Draws
            c.execute('''
                SELECT 
                    SUM(CASE WHEN player1 = ? AND result = '1-0' THEN 1
                            WHEN player2 = ? AND result = '0-1' THEN 1
                            ELSE 0 END) AS wins,
                    SUM(CASE WHEN player1 = ? AND result = '0-1' THEN 1
                            WHEN player2 = ? AND result = '1-0' THEN 1
                            ELSE 0 END) AS losses,
                    SUM(CASE WHEN (player1 = ? OR player2 = ?) AND result = '1/2-1/2' THEN 1
                            ELSE 0 END) AS draws
                FROM bd;
            ''', (name, name, name, name, name, name))

            wins, losses, draws = c.fetchone()

            c.execute('''
                SELECT 
                    SUBSTR(movements, 1, 25) AS opening_moves,
                    COUNT(*) AS opening_frequency
                FROM bd
                WHERE player1 = ?
                GROUP BY opening_moves
                ORDER BY opening_frequency DESC
            ''', (name,))

            # LIMIT 3; -- Change the limit based on how many top openings you want
            white_openings = c.fetchall()

            c.execute('''
                SELECT ELO1 AS elo, date
                FROM bd
                WHERE player1 = ?
                UNION ALL
                SELECT ELO2 AS elo, date
                FROM bd
                WHERE player2 = ?
            ''', (name, name))

            elo_dates = c.fetchall()

            # Remove entries with invalid date formats (replace '2001.??.??' with a placeholder)
            elo_dates = [(elo, date) for elo, date in elo_dates if '??' not in date]


            elo_dates = [(elo, datetime.strptime(date, '%Y.%m.%d')) for elo, date in elo_dates]

            # Sort elo_dates by date
            elo_dates.sort(key=lambda x: x[1])

            # Separate dates and ELOs for plotting
            dates = [date for elo, date in elo_dates]
            elos = [int(elo) for elo, date in elo_dates]
            
            unique_combinations = set()
            unique_dates = []
            unique_elos = []

            for a, b in zip(dates, elos):
                combination = (a, b)
                if combination not in unique_combinations:
                    unique_combinations.add(combination)
                    unique_dates.append(a)
                    unique_elos.append(b)

            for a, b in zip(unique_dates, unique_elos):
                print(a, b)

            conn.commit()
            conn.close()

            fig, ax = plt.subplots()

            if len(unique_elos) == 1:
                # If only one value, create a scatter plot
                ax.scatter(unique_dates, unique_elos, label="Elo", color='blue')
            else:
                # If multiple values, create a line plot
                ax.plot(unique_dates, unique_elos, label="Elo", color='blue')

            ax.plot(unique_dates, unique_elos, color='blue')
            ax.set_title("ELO")
            ax.set_xlabel("dates")
            ax.set_ylabel("elos")

            show_window = tk.Toplevel(self.root)
            show_window.geometry('1000x800')
            show_window.title(f"{name}")
    
            topframe_show = tk.Frame(show_window)
            topframe_show.pack(fill="both", expand=True)

            # Create the label
            etiqueta2 = ttk.Label(topframe_show, text=f"{name}", font=("Arial", 24))
            etiqueta2.pack(side="top", fill="both", expand=True)

            # Configure the label to center its contents
            etiqueta2.place(relx=0.5, rely=0.5, anchor="center")

            elo_show = tk.Frame(show_window)
            elo_show.pack(fill="both", expand=True)

            canvas = FigureCanvasTkAgg(fig, master=elo_show)
            canvas.draw()
            canvas.get_tk_widget().pack()



    def sorter(self, column, tree):

        """
        Sorts a column in a given treeview
        Args:
            self:
            column (int): given column of the treeview to sort
            tree (ttk.Treeview): given treeview to sort
        """

        def treeview_sort_column(tv, col, reverse, key=lambda t: t):
            column_index = col
            # 
            if col == 1 and tv == self.treeview_partidas:
                val_list = [(datetime.strptime(str(tv.item(k)["values"][column_index]), '%Y.%m.%d'), k) for k in tv.get_children('')]
            else:
                val_list = [(key(tv.item(k)["values"][column_index]), k) for k in tv.get_children('')]

            val_list.sort(key=lambda t: t[0], reverse=reverse)
            for index, (val, k) in enumerate(val_list):
                tv.move(k, '', index)
            tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse, key))

        column = int(column)

        if column not in self.sort_reverse:
            self.sort_reverse[column] = False

        treeview_sort_column(tree, column - 1, self.sort_reverse[column])

        self.sort_reverse[column] = not self.sort_reverse[column]



    def set_icon(self):

        """
        Sets an icon to be placed as the logo of the application
        Args:
            self:

        """

        self.ico_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"logo.ico")
        
        try:
            self.root.iconbitmap("piezas\logo.ico")
        except tk.TclError:
            pass


    def create_initial_db(self):

        """
        Creates the initial database
        Args:
            self:
        """

        conn = sqlite3.connect('bd.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS bd (
                id INTEGER PRIMARY KEY,
                event TEXT,
                date TEXT,
                ELO1 TEXT,
                player1 TEXT,
                result TEXT,
                player2 TEXT,
                ELO2 TEXT,
                movements TEXT
            )
        ''')
        conn.commit()
        conn.close()


    def add_game(self):

        """
        Opens a dialog to select a PGN file, parses it, and adds the parsed fields to the database. 
        Opens a new window to keep a counter with how many games are being added.

        Args:
            self:

        """

        path = filedialog.askopenfilename(filetypes=[("PGN files", "*.pgn")])
        counter = tk.IntVar()
        text = tk.StringVar()
        text.set("Number of PGNs added:")

        if path:
            conn = sqlite3.connect('bd.db')
            c = conn.cursor()

            with open(path) as pgn_file:

                counter_window = tk.Toplevel(self.root)
                counter_window.geometry('200x100')
                counter_window.title('Metiendo PGN')


                etiqueta2 = ttk.Label(counter_window, textvariable=text)
                etiqueta2.grid(column=0, row=0, padx=10, pady=10)

                etiqueta = ttk.Label(counter_window, textvariable=counter)
                etiqueta.grid(column=0, row=1, padx=10, pady=10)

                counter.set(0)

                while True:

                    partida = chess.pgn.read_game(pgn_file)

                    if partida is None:
                        break

                    blancas = partida.headers['White']
                    negras = partida.headers['Black']
                    resultado = partida.headers['Result']
                    elo_blancas = partida.headers['WhiteElo']
                    elo_negras = partida.headers['BlackElo']
                    fecha = partida.headers['Date']
                    evento = partida.headers['Event']
                    movements = list(partida.mainline_moves())

                    try:
                        datetime.strptime(fecha, '%Y.%m.%d')
                    except ValueError:
                        # If the date doesn't follow the format, skip to the next iteration
                        continue

                    movements_texto = ' '.join(str(move) for move in movements)

                    c.execute('''
                        INSERT INTO bd (event, date, ELO1, player1, result, player2, ELO2, movements)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                ''', 
                        (evento, fecha, elo_blancas, blancas, resultado, negras, elo_negras, movements_texto)
                    )

                    counter.set(counter.get() + 1)
                    text.set("Number of games added:")

                    self.root.update_idletasks()
                    counter_window.update_idletasks()


            conn.commit()
            conn.close()
            
            self.update_treeview()
            self.add_players()
            counter_window.destroy()

    def view_game(self):

        """
        With a game selected from treeview_partidas, it will open a window to visualize the board, movements and (optionally) interact with the module to provide a movement/game score

        Args:
            self:
        """
        
        if not self.treeview_partidas.selection():
            return
        board = chess.Board()

        item = self.treeview_partidas.selection()[0]
        item_data = self.treeview_partidas.item(item)
        id_name = item_data['text']

        conn = sqlite3.connect('bd.db')
        c = conn.cursor()

        c.execute('SELECT ELO1, player1, result, player2, ELO2, movements FROM bd WHERE id = ?', (id_name,))
        partida = c.fetchall()


        blancas = partida[0][1]
        negras = partida[0][3]
        resultado = partida[0][2]
        elo_blancas = partida[0][0]
        elo_negras = partida[0][4]
        movements = partida[0][5].split()

        parsed_moves = []
        for move_str in movements:
            move = chess.Move.from_uci(move_str)
            parsed_moves.append(move)

        index = 0
        text = tk.StringVar(value="No se ha hecho ningun movimiento")

        game_display = tk.Toplevel(self.root)
        game_display.title(f"({elo_blancas}) {blancas} - {resultado} - {negras} ({elo_negras})")
        game_display.minsize(600, 450)


        board_frame = tk.Frame(game_display)
        moves_frame = tk.Frame(game_display)
        module_frame = tk.Frame(game_display)
        empty_frame = tk.Frame(game_display)


        board_frame.grid(row=0, column=0, sticky='nsew')
        moves_frame.grid(row=0, column=1, sticky='nsew')
        module_frame.grid(row=1, column=0, sticky='nsew')
        empty_frame.grid(row=1, column=1, sticky='nsew')

        game_display.grid_rowconfigure(0, weight=1)
        game_display.grid_rowconfigure(1, weight=1)
        game_display.grid_columnconfigure(0, weight=1)
        game_display.grid_columnconfigure(1, weight=1)

        canvas = tk.Canvas(board_frame, width=400, height=400)
        canvas.pack()

        def next_move():

            """
            Performs the next move on the board
            """

            nonlocal index
            if index < len(parsed_moves):
                board.push(parsed_moves[index])
                index += 1
                text.set(f"{str((index - 1) // 2 + 1)} {str(parsed_moves[index - 1])}")

                draw_board(canvas, board, self.script_dir, self.images)



        def previous_move():

            """
            Performs the previous move on the board
            """

            nonlocal index
            if index > 0:
                index -= 1
                text.set(f"{str((index - 1) // 2 + 1)} {str(parsed_moves[index - 1])}")
                board.pop()
                draw_board(canvas, board, self.script_dir, self.images)



        scrollbar = tk.Scrollbar(moves_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        treeview2= ttk.Treeview(moves_frame, yscrollcommand=scrollbar.set)
        treeview2['columns'] = ("Turno", "Blancas", "Negras")


        treeview2.column("#0", width=0, stretch=tk.NO)
        treeview2.column("Turno", anchor=tk.W, width=40)
        treeview2.column("Blancas", anchor=tk.W, width=60)
        treeview2.column("Negras", anchor=tk.W, width=60)


        treeview2.heading("#0", text="", anchor=tk.W)
        treeview2.heading("Turno", text="Turno", anchor=tk.W)
        treeview2.heading("Blancas", text="Blancas", anchor=tk.W)
        treeview2.heading("Negras", text="Negras", anchor=tk.W)   


        for i in range(0, len(parsed_moves), 2):
            turno = i // 2 + 1
            movimiento_blancas = parsed_moves[i]
            movimiento_negras = parsed_moves[i + 1] if i + 1 < len(parsed_moves) else ''
            treeview2.insert('', 'end', text=str(turno), values=(turno, movimiento_blancas, movimiento_negras))

        def selec_module():

            """
            Pops a file select window to select a module, if the user wants
            """

            modulo = filedialog.askopenfilename()
            self.engine = chess.engine.SimpleEngine.popen_uci(modulo)


        def update_label():

            """
            If a module was selected, calls the module to analyse the position and returns a label with the 3 best moves and their scores
            """

            if self.engine:

                info = self.engine.analyse(board, limit=chess.engine.Limit(time=0.1), multipv=3)
                top_moves = [info[var]["pv"][0] for var in range(3)]
                top_scores = [info[var]["score"].relative.score()/100 for var in range(3)]

                text = ""
                for i, move in enumerate(top_moves):
                    text += f"{i+1}. {move} ({top_scores[i]:+.2f})\n"
                label3.config(text=text)


        def prev():

            """
            Used as a caller helper for the button previous, performs the previous move calling previous_move() and updates the label calling update_label()
            """

            previous_move()
            update_label()


        def next():

            """
            Used as a caller helper for the button next, performs the previous move calling next_move() and updates the label calling update_label()
            """

            next_move()
            update_label()   

        btn_previous_move = tk.Button(board_frame, text="Previous", command=prev)
        btn_previous_move.pack(side=tk.LEFT)

        btn_next_move = tk.Button(board_frame, text="Next", command=next)
        btn_next_move.pack(side=tk.LEFT)

        btn_previous_move = tk.Button(board_frame, text="Modulo", command=selec_module)
        btn_previous_move.pack(side=tk.LEFT)

        label2 = tk.Label(board_frame, textvariable="   ")
        label2.pack(side=tk.LEFT)

        label = tk.Label(board_frame, textvariable=text)
        label.pack(side=tk.LEFT)


        label3 = tk.Label(module_frame, text="")
        label3.pack(side=tk.LEFT)

        scrollbar.config(command=treeview2.yview)

        treeview2.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        draw_board(canvas, board, self.script_dir, self.images)

        game_display.mainloop()

 

    def delete_game(self):

        """
        Deletes a selected game from the database

        Args:
            self:

        """

        if self.treeview_partidas.selection():
            item = self.treeview_partidas.selection()[0]
            item_data = self.treeview_partidas.item(item)
            id_name = item_data['text']

            conn = sqlite3.connect('bd.db')
            c = conn.cursor()

            try:
                c.execute('DELETE FROM bd WHERE id = ?', (id_name,))
            except Exception as e:
                print(f"Error: {e}")
                
            conn.commit()
            conn.close()

            self.treeview_partidas.delete(item)
            self.add_players()


    def update_treeview(self):
        
        """
        Updates the treeview with all the games from the database

        Args:
            self:

        """

        conn = sqlite3.connect('bd.db')
        c = conn.cursor()

        c.execute('SELECT id, event, date, ELO1, player1, result, player2, ELO2 FROM bd')
        datos = c.fetchall()

        for i in self.treeview_partidas.get_children():
            self.treeview_partidas.delete(i)  

        
        for dato in datos:
            blancas = dato[4]
            negras = dato[6]
            resultado = dato[5]
            elo_blancas = dato[3]
            elo_negras = dato[7]
            fecha = dato[2]
            evento = dato[1]

            self.treeview_partidas.insert('', 'end', text=str(dato[0]), values=(evento, fecha, elo_blancas, blancas, resultado, negras, elo_negras))

        conn.commit()
        conn.close()    

    def close_app(self):
        
        """
        Closes the app and windows. If a module was selected, quits the module.

        Args:
            self:

        """

        if self.engine:
            self.engine.close()
        self.root.quit()
        self.root.destroy()

def draw_board(canvas, board, script_dir, images):
    
    """
    Draws a chessboard and its pieces on a canvas

    Args:
        canvas (tk.Canvas()): tkinter canvas where the chess board will be drawn
        board (chess.Board()): board state to be represented in the canvas
        images (dictionary): dictionary which contains the loaded images
    """
    
    canvas.delete("all")
    
    for i in range(8):
        for j in range(8):
            color = 'white' if (i+j)%2 == 0 else 'gray'
            canvas.create_rectangle(i*50, j*50, (i+1)*50, (j+1)*50, fill=color)

    for i in range(8):
        for j in range(8):
            piece = board.piece_at(chess.square(i, 7-j))
            if piece is not None:
                if piece.color == chess.WHITE:
                    # filename = os.path.join(script_dir, "piezas", f"white_{str(piece)}.png")
                    filename = os.path.join("piezas", f"white_{str(piece)}.png")
                else:
                    # filename = os.path.join(script_dir, "piezas", f"black_{str(piece)}.png")
                    filename = os.path.join("piezas", f"black_{str(piece)}.png")
                
                try:
                    image = Image.open(filename)
                    image = image.resize((50, 50), Image.ANTIALIAS)
                    photo = ImageTk.PhotoImage(image)
                    images[(i, j)] = photo
                    canvas.create_image(i*50+25, j*50+25, image=photo)

                except Exception as e:
                    print(f"Error loading image: {e}") 

def main():
    
    """
    Main function, creates a window with tk.Tk, creates the ChessApp and launches the mainloop.
    """

    window = tk.Tk()
    app = ChessApp(window)
    window.protocol("WM_DELETE_WINDOW", app.close_app)
    window.mainloop()

if __name__ == "__main__":
    main()
