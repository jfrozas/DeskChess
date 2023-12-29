import sys
sys.path.append('../DeskChess')
import sqlite3
import unittest
import tkinter as tk
import src.app as app

class TestChessAppTkinter(unittest.TestCase):
    def setUp(self):
        # Connect to the SQLite database
        self.conn = sqlite3.connect('bd.db')
        self.cursor = self.conn.cursor()

        # SQL command to delete all records from the table
        delete_query = "DELETE FROM bd"

        # Execute the delete query
        self.cursor.execute(delete_query)

        # Commit the changes
        self.conn.commit()

    def tearDown(self):
        # Close the connection
        self.conn.close()
        # Add any additional cleanup if needed

    def test_empty(self):
        window = tk.Tk()
        testAp = app.ChessApp(window)
        self.assertEqual(testAp.treeview_partidas.get_children(), ())

if __name__ == "__main__":
    unittest.main()