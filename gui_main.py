import customtkinter as ctk
from tkinter import messagebox
import random

from GUI.main_menu import MainMenu
from game.codenames import Codenames, Phase
from GUI.codenames_gui import CodenamesGui

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")



if __name__ == "__main__":
    app = MainMenu()
    app.mainloop()