import logging
import os
import threading
from tkinter import messagebox

import customtkinter as ctk
import random

from GUI.codenames_gui import CodenamesGui
from game.codenames import Codenames
from game.game_runner import GameRunner
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
        self.geometry("1200x900")
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

        btn_gen = ctk.CTkButton(self.frame_other, text="Generate Dataset", command=self.generate_dataset)
        btn_gen.pack(pady=5)

        self.btn_batch = ctk.CTkButton(self.frame_other, text="Batch Evaluation", command=self.run_batch_evaluation)
        self.btn_batch.pack(pady=5)

        btn_view_batch = ctk.CTkButton(self.frame_other, text="View Evaluation Results", command=self.open_batch_results_dialog)
        btn_view_batch.pack(pady=5)

        btn_rep = ctk.CTkButton(self.frame_other, text="Watch replay", command=self.watch_replay)
        btn_rep.pack(pady=(5, 15))

    def watch_replay(self):
        import gzip
        import pickle
        from tkinter import filedialog


        filepath = filedialog.askopenfilename(
            initialdir=os.path.abspath("stats"),
            title="Select Replay File",
            filetypes=(("Gzip Pickle", "*.pkl.gz"), ("All Files", "*.*"))
        )

        if not filepath:
            return

        try:

            with gzip.open(filepath, "rb") as f:
                data = pickle.load(f)

            from GUI.replay_gui import ReplayGui
            self.destroy()
            app = ReplayGui(data)
            app.mainloop()

        except Exception as e:
            messagebox.showerror("Replay Error", f"Couldnt load replay:\n{str(e)}")
    def run_batch_evaluation(self):
        dataset_path = "data/boards_dataset.json"
        if not os.path.exists(dataset_path):
            messagebox.showerror("Error", f"coulnt find dataset at {dataset_path}. Generate it first.")
            return

        dialog = ctk.CTkInputDialog(text="Enter test name (np. test_glove_v1):", title="Batch Evaluation")
        run_name = dialog.get_input()

        if not run_name or not run_name.strip():
            return

        run_name = run_name.strip()

        self.btn_batch.configure(state="disabled", text="Evaluating... Please wait")


        thread = threading.Thread(target=self._evaluation_thread, args=(run_name, dataset_path), daemon=True)
        thread.start()

    def _evaluation_thread(self, run_name, dataset_path):
        stats_base_dir = "stats"
        run_dir = os.path.join(stats_base_dir, run_name)
        os.makedirs(run_dir, exist_ok=True)

        csv_path = os.path.join(run_dir, "batch_evaluation.csv")
        replays_dir = os.path.join(run_dir, "replays")
        os.makedirs(replays_dir, exist_ok=True)

        log_file_path = os.path.join(run_dir, "errors_and_warnings.log")
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8", mode="w")
        file_handler.setLevel(logging.WARNING)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)

        try:
            boards = DatasetManager.load_dataset(dataset_path)
            logging.getLogger().setLevel(logging.WARNING)

            for board_id, board in boards:
                game = Codenames(pregenerated_board=board)
                spymaster = GloveSpyMaster()
                guesser = GloveGuesser()

                eval_logger = GameLogger(spymaster.__class__.__name__, guesser.__class__.__name__, board_id=str(board_id))
                runner = GameRunner(spymaster, guesser, game, render=False, game_logger=eval_logger)
                runner.run()

                eval_logger.save_stats_to_csv(csv_path)

                game_number = int(board_id) + 1
                eval_logger.save_binary_replay(replays_dir, custom_filename=f"replay_game_{game_number}.pkl.gz")

            status_message = f"Evaluation successed!\nData saved in:\n{run_dir}/"
            status_title = "Succssess"

        except Exception as e:
            status_message = f"Error during evaluation: {e}"
            status_title = "Error"
        finally:
            logging.getLogger().setLevel(logging.INFO)


            def update_ui():
                self.btn_batch.configure(state="normal", text="Batch Evaluation")
                if status_title == "Succssess":
                    messagebox.showinfo(status_title, status_message)

                    from GUI.batch_result_gui import BatchResultsGui
                    self.destroy()
                    app = BatchResultsGui(run_name)
                    app.mainloop()
                else:
                    messagebox.showerror(status_title, status_message)

            self.after(0, update_ui)

    def open_batch_results_dialog(self):
        stats_dir = "stats"
        if not os.path.exists(stats_dir):
            messagebox.showinfo("Info", "No stats folder found.")
            return

        runs = [d for d in os.listdir(stats_dir) if os.path.isdir(os.path.join(stats_dir, d)) and d != "single_games"]

        if not runs:
            messagebox.showinfo("Info", "No batch evaluation runs found.")
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Select Evaluation")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()

        lbl = ctk.CTkLabel(dialog, text="Select or type test name:", font=ctk.CTkFont(size=14, weight="bold"))
        lbl.pack(pady=(20, 10))

        combo_var = ctk.StringVar(value=runs[0])
        combo = ctk.CTkComboBox(dialog, values=runs, variable=combo_var, width=250)
        combo.pack(pady=10)

        def confirm():
            selected = combo_var.get().strip()
            if not selected: return

            if not os.path.exists(os.path.join(stats_dir, selected)):
                messagebox.showerror("Error", f"Run '{selected}' does not exist.")
                return

            dialog.destroy()
            from GUI.batch_result_gui import BatchResultsGui
            self.destroy()
            app = BatchResultsGui(selected)
            app.mainloop()

        btn_confirm = ctk.CTkButton(dialog, text="Open", command=confirm)
        btn_confirm.pack(pady=10)
    def generate_dataset(self):
        words_file_path = "data/words.txt"
        dataset_path = "data/boards_dataset.json"

        try:
            with open(words_file_path, 'r', encoding='utf-8') as f:
                words_pool = [line.strip().upper() for line in f if line.strip()]
        except FileNotFoundError:
            messagebox.showerror("Error", f"File cant be find: {words_file_path}")
            return

        if len(words_pool) < 25:
            messagebox.showerror("Error", "not enough words in dict (min 25).")
            return

        if os.path.exists(dataset_path):
            confirm = messagebox.askyesno(
                "Dataset already exists",
                f"dataset already exists at '{dataset_path}'.\nAre you sure you want to overwrite it?"
            )
            if not confirm:
                return

        try:
            os.makedirs(os.path.dirname(dataset_path), exist_ok=True)

            DatasetManager.generate_and_save_dataset(words_pool, 100, dataset_path)
            messagebox.showinfo("Success", "Succesfully generated dataset!")
        except Exception as e:
            messagebox.showerror("Error", f"Error occured during dataset generation: {str(e)}")


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
