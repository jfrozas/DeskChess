import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import chess.pgn
import chess.engine
import os
from PIL import ImageTk, Image



def draw_board(canvas, board, script_dir, images):
    
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
                    filename = os.path.join(script_dir, "piezas", f"white_{str(piece)}.png")
                else:
                    filename = os.path.join(script_dir, "piezas", f"black_{str(piece)}.png")
                
                try:
                    image = Image.open(filename)
                    image = image.resize((50, 50), Image.ANTIALIAS)
                    photo = ImageTk.PhotoImage(image)
                    images[(i, j)] = photo
                    canvas.create_image(i*50+25, j*50+25, image=photo)

                except Exception as e:
                    print(f"Error loading image: {e}") 