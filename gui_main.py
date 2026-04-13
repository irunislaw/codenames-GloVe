import customtkinter as ctk
from tkinter import messagebox
import random

from GUI.main_menu import MainMenu
from game.codenames import Codenames, Phase
from GUI.codenames_gui import CodenamesGui

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


#TODO w replayu zeby byl debug mode albo pokazalo cosine similatiy z glovea
#TODO szybkie statystyki dla testu winrate srednia liczba tur, glowne powody przegranej
#TODO autoplay w repleyaru
#TODO sortowanie po kolumnach
#TODO moze filtr
#TODO mozliwosc zagrania konkretnej planszy samemu
#TODO moze jakas wizualizacja wektorów
#TODO rozne stopnie trudnosci(zmiana liczb neutralnych)

if __name__ == "__main__":
    app = MainMenu()
    app.mainloop()