import os
import csv
import gzip
import pickle
import tkinter as tk  # Importujemy standardowe tkinter dla PanedWindow
from tkinter import ttk, messagebox
from typing import Tuple

import customtkinter as ctk

from GUI.replay_gui import ReplayFrame


class BatchResultsGui(ctk.CTk):
    def __init__(self, run_name):
        super().__init__()
        self.title(f"Batch Evaluation Results - {run_name}")
        self.geometry("1400x800")
        self.run_name = run_name
        self.run_dir = os.path.join("stats", run_name)
        self.csv_path = os.path.join(self.run_dir, "batch_evaluation.csv")
        self.current_replay_frame = None


        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)


        self.paned_window = tk.PanedWindow(
            self,
            orient="horizontal",
            bg="#1a1a1a",
            bd=0,
            sashwidth=6,
            sashcursor="sb_h_double_arrow"
        )
        self.paned_window.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.setup_styles()


        self.setup_left_panel()
        self.setup_right_panel()

        self.paned_window.add(self.left_frame, stretch="always", width=700)
        self.paned_window.add(self.right_frame, stretch="always", width=700)

        self.after(50,  self.center_paned_window)

    def center_paned_window(self):
        current_width = self.winfo_width()
        if current_width > 100:
            self.paned_window.sash_place(0, current_width // 2, 0)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#2a2d2e", foreground="white", rowheight=25,
                        fieldbackground="#2a2d2e", bordercolor="#343638", borderwidth=0)
        style.map('Treeview', background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading", background="#343638", foreground="white", relief="flat",
                        font=('Helvetica', 10, 'bold'))
        style.map("Treeview.Heading", background=[('active', '#1f538d')])

    def setup_left_panel(self):

        self.left_frame = ctk.CTkFrame(self.paned_window, corner_radius=0)
        self.left_frame.grid_rowconfigure(1, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        top_bar = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        btn_back = ctk.CTkButton(top_bar, text="⬅ Menu", command=self.return_to_menu, fg_color="#c0392b",
                                 hover_color="#922b21", width=100)
        btn_back.pack(side="left")

        lbl_title = ctk.CTkLabel(top_bar, text=f"Data: {self.run_name}", font=ctk.CTkFont(size=16, weight="bold"))
        lbl_title.pack(side="left", padx=15)

        self.tree_frame = ctk.CTkFrame(self.left_frame)
        self.tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self.tree_scroll_y = ttk.Scrollbar(self.tree_frame, orient="vertical")
        self.tree_scroll_y.pack(side="right", fill="y")
        self.tree_scroll_x = ttk.Scrollbar(self.tree_frame, orient="horizontal")
        self.tree_scroll_x.pack(side="bottom", fill="x")

        self.tree = ttk.Treeview(self.tree_frame, yscrollcommand=self.tree_scroll_y.set,
                                 xscrollcommand=self.tree_scroll_x.set)
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree_scroll_y.config(command=self.tree.yview)
        self.tree_scroll_x.config(command=self.tree.xview)
        self.tree.bind("<Double-1>", self.on_row_double_click)
        self.load_csv_data()

    def setup_right_panel(self):
        self.right_frame = ctk.CTkFrame(self.paned_window, corner_radius=0)
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        self.lbl_empty = ctk.CTkLabel(self.right_frame, text="⬅ Kliknij dwukrotnie w tabelę,\naby załadować powtórkę.",
                                      font=ctk.CTkFont(size=18))
        self.lbl_empty.grid(row=0, column=0)

    def load_csv_data(self):
        if not os.path.exists(self.csv_path): return
        with open(self.csv_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            self.tree["columns"] = headers
            self.tree["show"] = "headings"
            for h in headers:
                self.tree.heading(h, text=h)
                self.tree.column(h, width=100, anchor="center")
            for row in reader:
                self.tree.insert("", "end", values=row)

    def on_row_double_click(self, event):
        selected = self.tree.selection()
        if not selected: return
        item = self.tree.item(selected[0])
        values = item["values"]
        headers = self.tree["columns"]

        board_id_idx = 0
        for i, h in enumerate(headers):
            if h.lower() in ["board_id", "boardid", "id"]:
                board_id_idx = i
                break

        board_id = str(values[board_id_idx])
        try:
            game_number = int(board_id) + 1
        except:
            game_number = board_id

        replay_path = os.path.join(self.run_dir, "replays", f"replay_game_{game_number}.pkl.gz")
        if os.path.exists(replay_path):
            self.load_replay(replay_path)
        else:
            messagebox.showwarning("Błąd", "Nie znaleziono pliku powtórki.")

    def load_replay(self, replay_path):
        try:
            with gzip.open(replay_path, "rb") as f:
                data = pickle.load(f)
            if self.current_replay_frame:
                self.current_replay_frame.destroy()
            self.lbl_empty.grid_forget()

            self.current_replay_frame = ReplayFrame(self.right_frame, data)
            self.current_replay_frame.pack(fill="both", expand=True, padx=5, pady=5)
        except Exception as e:
            messagebox.showerror("Error", f"Nie udało się załadować: {e}")

    def return_to_menu(self):
        from GUI.main_menu import MainMenu
        self.destroy()
        app = MainMenu()
        app.mainloop()