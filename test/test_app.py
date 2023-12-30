import sys
sys.path.append('../DeskChess')

import tkinter as tk
from src import app

def test_init():
    window = tk.Tk()
    c = app.ChessApp(window)
    assert c.engine == None
    assert c.images == {}
    assert c.sort_reverse == {}