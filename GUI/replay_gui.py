import customtkinter as ctk


class ReplayFrame(ctk.CTkFrame):
    def __init__(self,master, replay_data, **kwargs):
        super().__init__(master, **kwargs)
        self.replay_data = replay_data
        self.history = replay_data["history"]
        self.current_step = 0

        self.COLOR_UNKNOWN = "#3b3b3b"
        self.COLOR_TARGET = "#2ecc71"
        self.COLOR_NEUTRAL = "#d3aa76"
        self.COLOR_ASSASSIN = "#e74c3c"

        self.setup_ui()
        self.update_board()

    def get_color(self, card_type):
        if card_type == "TARGET": return self.COLOR_TARGET
        if card_type == "NEUTRAL": return self.COLOR_NEUTRAL
        if card_type == "ASSASSIN": return self.COLOR_ASSASSIN
        return self.COLOR_UNKNOWN

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)


        self.board_frame = ctk.CTkFrame(self)
        self.board_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        for i in range(5):
            self.board_frame.grid_columnconfigure(i, weight=1)
            self.board_frame.grid_rowconfigure(i, weight=1)

        self.buttons = {}
        row, col = 0, 0
        for word, card_type in self.replay_data["initial_board"]:
            btn = ctk.CTkButton(
                self.board_frame,
                text=f"{word}\n",
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color=self.COLOR_UNKNOWN,
                text_color="white",
                corner_radius=8,
                state="disabled"
            )
            btn.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            self.buttons[word] = btn
            col += 1
            if col > 4:
                col = 0
                row += 1


        self.right_panel = ctk.CTkFrame(self, width=350)
        self.right_panel.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
        self.right_panel.grid_rowconfigure(1, weight=1)


        self.controls_frame = ctk.CTkFrame(self.right_panel)
        self.controls_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.btn_prev = ctk.CTkButton(self.controls_frame, text="< Prev", command=self.prev_step, width=80)
        self.btn_prev.pack(side="left", padx=5, pady=10)

        self.step_label = ctk.CTkLabel(self.controls_frame, text=f"Step: 0 / {len(self.history)}",
                                       font=ctk.CTkFont(weight="bold"))
        self.step_label.pack(side="left", expand=True)

        self.btn_next = ctk.CTkButton(self.controls_frame, text="Next >", command=self.next_step, width=80)
        self.btn_next.pack(side="right", padx=5, pady=10)


        self.timeline_frame = ctk.CTkScrollableFrame(self.right_panel, label_text="Match Timeline")
        self.timeline_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self.log_labels = []
        for i, action in enumerate(self.history):
            if action["action"] == "CLUE":
                text = f"🎯 Clue: {action['clue']} ({action['count']})"
                color = "#5dade2"
            else:
                word = action["word"]
                if word == "PASS":
                    text = "⏭️ Guesser PASSED"
                    color = "white"
                else:
                    res = action["result"]
                    text = f"❓ Guess: {word} -> {res}"
                    if res == "TARGET":
                        color = self.COLOR_TARGET
                    elif res == "ASSASSIN":
                        color = self.COLOR_ASSASSIN
                    elif res == "NEUTRAL":
                        color = self.COLOR_NEUTRAL
                    else:
                        color = "white"

            lbl = ctk.CTkLabel(self.timeline_frame, text=text, text_color=color, anchor="w", font=ctk.CTkFont(size=14))
            lbl.pack(fill="x", pady=2, padx=5)
            self.log_labels.append(lbl)


        self.options_frame = ctk.CTkFrame(self.right_panel)
        self.options_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)

        self.spymaster_view_var = ctk.BooleanVar(value=True)
        self.spymaster_cb = ctk.CTkCheckBox(self.options_frame, text="Spymaster View (Pokaż kolory)", variable=self.spymaster_view_var, command=self.update_board)
        self.spymaster_cb.pack(pady=10)




    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.update_board()

    def next_step(self):
        if self.current_step < len(self.history):
            self.current_step += 1
            self.update_board()

    def update_board(self):
        self.step_label.configure(text=f"Step: {self.current_step} / {len(self.history)}")


        revealed_words = set()
        for i in range(self.current_step):
            action = self.history[i]
            if action["action"] == "GUESS" and action["word"] != "PASS":
                revealed_words.add(action["word"])


        for word, card_type in self.replay_data["initial_board"]:
            btn = self.buttons[word]
            actual_color = self.get_color(card_type)

            if word in revealed_words:

                btn.configure(fg_color=actual_color, text=f"{word}\n[X]", text_color="black")
            else:

                if self.spymaster_view_var.get():

                    btn.configure(fg_color=actual_color, text=f"{word}\n", text_color="black")
                else:

                    btn.configure(fg_color=self.COLOR_UNKNOWN, text=f"{word}\n", text_color="white")


        for i, lbl in enumerate(self.log_labels):
            if i == self.current_step - 1:
                lbl.configure(fg_color="#555555", corner_radius=5)
            else:
                lbl.configure(fg_color="transparent")


class ReplayGui(ctk.CTk):


    def __init__(self, replay_data):
        super().__init__()
        self.title("Codenames - Replay Viewer")
        self.geometry("1100x650")

        self.replay_frame = ReplayFrame(self, replay_data)
        self.replay_frame.pack(fill="both", expand=True)


        self.btn_back = ctk.CTkButton(self.replay_frame.options_frame, text="Return to Menu",
                                      fg_color="#c0392b", hover_color="#922b21", command=self.return_to_menu)
        self.btn_back.pack(pady=(10, 5))

    def return_to_menu(self):
        from GUI.main_menu import MainMenu
        self.destroy()
        app = MainMenu()
        app.mainloop()