import os
from tkinter import messagebox

import customtkinter as ctk
import random

from GUI.codenames_gui import CodenamesGui
from game.codenames import Codenames
from players.glove_guesser import GloveGuesser
from players.glove_spymaster import GloveSpyMaster
from utils.dataset_manager import DatasetManager
from utils.game_logger import GameLogger

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
class MainMenu(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Codenames - Main Menu")
        self.geometry("600x450")
        self.grid_columnconfigure(0, weight=1)
        title_label = ctk.CTkLabel(self, text="=== CODENAMES ===", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=0, pady=(20, 10))

        self.frame_single_game = ctk.CTkFrame(self)
        self.frame_single_game.grid(row=1, column=0, padx=40, pady=10, sticky="ew")
        self.frame_single_game.grid_columnconfigure((0, 1), weight=1)

        label_sg = ctk.CTkLabel(self.frame_single_game, text="Play a single game:", font=ctk.CTkFont(size=16, weight="bold"))
        label_sg.grid(row=0, column=0, columnspan=2, pady=10)

        label_sm = ctk.CTkLabel(self.frame_single_game, text="Spymaster:")
        label_sm.grid(row=1, column=0, pady=5, padx=10, sticky="e")
        self.var_sm = ctk.StringVar(value="Human")
        self.combo_sm = ctk.CTkComboBox(self.frame_single_game, values=["Human", "Glove Bot"], variable=self.var_sm)
        self.combo_sm.grid(row=1, column=1, pady=5, padx=10, sticky="w")

        label_g = ctk.CTkLabel(self.frame_single_game, text="Guesser:")
        label_g.grid(row=2, column=0, pady=5, padx=10, sticky="e")
        self.var_g = ctk.StringVar(value="Human")
        self.combo_g = ctk.CTkComboBox(self.frame_single_game, values=["Human", "Glove Bot"], variable=self.var_g)
        self.combo_g.grid(row=2, column=1, pady=5, padx=10, sticky="w")

        self.var_dataset = ctk.BooleanVar(value=False)
        self.check_dataset = ctk.CTkCheckBox(self.frame_single_game, text="Load random board from Dataset",variable=self.var_dataset)
        self.check_dataset.grid(row=3, column=0, columnspan=2, pady=10)

        btn_start = ctk.CTkButton(self.frame_single_game, text="Play", command=self.start_single_game)
        btn_start.grid(row=4, column=0, columnspan=2, pady=15)

        self.frame_other = ctk.CTkFrame(self)
        self.frame_other.grid(row=2, column=0, padx=40, pady=10, sticky="ew")

        label_other = ctk.CTkLabel(self.frame_other, text="Other options:",
                                   font=ctk.CTkFont(size=16, weight="bold"))
        label_other.pack(pady=10)

        btn_gen = ctk.CTkButton(self.frame_other, text="Generate Dataset", state="disabled")
        btn_gen.pack(pady=5)

        btn_rep = ctk.CTkButton(self.frame_other, text="watch replay", state="disabled")
        btn_rep.pack(pady=(5, 15))

    def start_single_game(self):
        sm_type = self.var_sm.get()
        g_type = self.var_g.get()
        spymaster = GloveSpyMaster() if sm_type == "Glove Bot" else None
        guesser = GloveGuesser() if g_type == "Glove Bot" else None
        if self.var_dataset.get():
            dataset_path = "data/boards_dataset.json"
            if not os.path.exists(dataset_path):
                messagebox.showerror("Error", f"Dataset not found at {dataset_path}. Generate it first.")
                return
            boards = DatasetManager.load_dataset(dataset_path)
            board_id, board = random.choice(boards)
            my_game = Codenames(pregenerated_board=board)
        else:
            try:
                with open("data/words.txt", 'r', encoding='utf-8') as f:
                    words_pool = [line.strip().upper() for line in f if line.strip()]
            except FileNotFoundError:
                messagebox.showerror("Error", "Couldnt find data/words.txt!")
                return

            if len(words_pool) < 25:
                messagebox.showerror("Error", "Not enough words in dict (min 25).")
                return

            board_id = "random_generation"
            my_game = Codenames(words=random.sample(words_pool, 25))
        print(f"[MENU] preparing game: Spymaster={sm_type}, Guesser={g_type}")
        sm_name = spymaster.__class__.__name__ if spymaster else "HumanSpyMaster"
        g_name = guesser.__class__.__name__ if guesser else "HumanGuesser"
        eval_logger = GameLogger(sm_name, g_name, board_id=board_id)


        self.destroy()
        app = CodenamesGui(my_game, spymaster,guesser, eval_logger)
        app.mainloop()
