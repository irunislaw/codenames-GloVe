import logging
import os
from tkinter import messagebox
import customtkinter as ctk
from game.codenames import Codenames, Phase
class CodenamesGui(ctk.CTk):
    def __init__(self, game: Codenames, spymaster=None, guesser=None, game_logger=None):
        super().__init__()
        self.game = game
        self.spymaster = spymaster
        self.guesser = guesser
        self.game_logger = game_logger
        self.consecutive_errors = 0
        self.MAX_ERRORS = 3
        self.setup_logging()
        if self.game_logger:
            self.game_logger.set_initial_board(self.game.board)
        self.bot_action_scheduled = False
        self.title("Codenames")
        self.geometry("1000x600")
        self.COLOR_UNKNOWN = "#3b3b3b"
        self.COLOR_TARGET = "#2ecc71"
        self.COLOR_NEUTRAL = "#d3aa76"
        self.COLOR_ASSASSIN = "#e74c3c"

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.buttons = {}
        self.setup_board_ui()
        self.setup_control_panel_ui()
        self.update_ui()

    def setup_logging(self):
        os.makedirs("stats/single_games", exist_ok=True)
        self.logger = logging.getLogger("CodenamesGUI")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            log_path = os.path.join("stats", "single_games", "errors_and_warnings.log")
            file_handler = logging.FileHandler(log_path, encoding="utf-8", mode="a")
            file_handler.setLevel(logging.WARNING)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def setup_board_ui(self):

        self.board_frame = ctk.CTkFrame(self)
        self.board_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")


        for i in range(5):
            self.board_frame.grid_columnconfigure(i, weight=1)
            self.board_frame.grid_rowconfigure(i, weight=1)

        row, col = 0, 0
        for card in self.game.board:
            btn = ctk.CTkButton(
                self.board_frame,
                text=f"{card.word}\n",
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color=self.COLOR_UNKNOWN,
                text_color="white",
                corner_radius=8,
                command=lambda w=card.word: self.on_card_click(w)
            )
            btn.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            self.buttons[card.word] = btn

            col += 1
            if col > 4:
                col = 0
                row += 1

    def setup_control_panel_ui(self):
        self.control_frame = ctk.CTkFrame(self, width=250)
        self.control_frame.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
        self.control_frame.pack_propagate(False)
        self.info_label = ctk.CTkLabel(self.control_frame, text="Spymaster turn",
                                       font=ctk.CTkFont(size=18, weight="bold"),
                                       wraplength=230)
        self.info_label.pack(pady=(20, 10))


        self.score_label = ctk.CTkLabel(self.control_frame, text="Remaining cards: 9", font=ctk.CTkFont(size=14))
        self.score_label.pack(pady=5)
        self.clue_input_frame = ctk.CTkFrame(self.control_frame, fg_color="transparent")

        self.clue_entry = ctk.CTkEntry(self.clue_input_frame, placeholder_text="Enter clue", width=160)
        self.clue_entry.pack(pady=5)

        self.count_entry = ctk.CTkEntry(self.clue_input_frame, placeholder_text="Word count", width=160)
        self.count_entry.pack(pady=5)

        self.submit_btn = ctk.CTkButton(self.clue_input_frame, text="Confirm clue", width=160, command=self.submit_clue)
        self.submit_btn.pack(pady=10)

        self.pass_btn = ctk.CTkButton(self.control_frame, text="End turn", fg_color="gray", hover_color="#555555",
                                      width=160, command=self.pass_turn)
        self.pass_btn.pack(pady=20)




    def submit_clue(self):
        clue = self.clue_entry.get().strip()
        try:
            count = int(self.count_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for word count.")
            return

        success, msg = self.game.give_clue(clue, count)
        if success:
            self.consecutive_errors = 0
            if self.game_logger:
                self.game_logger.log_clue(clue, count)
            self.clue_entry.delete(0, 'end')
            self.count_entry.delete(0, 'end')

            self.update_ui()
        else:
            self.consecutive_errors += 1
            messagebox.showwarning("Incorrect word ", msg)

    def pass_turn(self):
        self.consecutive_errors = 0
        self.game.end_guessing_early()
        if self.game_logger:
            self.game_logger.log_guess("PASS", "PASS")
        self.update_ui()

    def on_card_click(self, word: str):
        if self.game.phase != Phase.GUESSING or self.guesser is not None:
            messagebox.showinfo("Caution!", "Its spymaster's turn.")
            return
        card_type = next((c.card_type.value for c in self.game.board if c.word == word), "UNKNOWN")
        success, msg = self.game.guess(word)
        if not success:
            self.consecutive_errors += 1
            return
        self.consecutive_errors = 0
        if self.game_logger:
            self.game_logger.log_guess(word, card_type)

        self.check_game_over()
        self.update_ui()

    def check_game_over(self):
        if self.game.phase == Phase.GAME_OVER:
            if self.game_logger:
                self.game_logger.finalize_game(self.game)
                single_csv = os.path.join("stats", "single_games", "single_games.csv")
                single_replay_dir = os.path.join("stats", "single_games", "replays")
                self.game_logger.save_stats_to_csv(single_csv)
                self.game_logger.save_binary_replay(single_replay_dir)
            self.update_ui()
            self.update()
            if self.consecutive_errors >= self.MAX_ERRORS:
                messagebox.showerror("Disqualified", "Game Over!\n\nBot was disqualified after 3 invalid attempts.")
            elif self.game.is_victory:
                messagebox.showinfo("Game Over", f"You Won in {self.game.turn_taken} turns!\n\nStats and replay saved.")
            else:
                messagebox.showerror("Game Over", "BOOM! You hit an assassin card.\n\nStats and replay saved.")


    def execute_bot_spymaster(self):
        obs = self.game.get_observation_for_spymaster()
        clue, count = self.spymaster.get_clue(obs)

        success, msg = self.game.give_clue(clue, count)
        if success:
            self.consecutive_errors = 0
            self.logger.info(f"Bot Spymaster gave clue: ({clue}, {count})")
            if self.game_logger:
                self.game_logger.log_clue(clue, count)
        else:
            self.consecutive_errors += 1
            self.logger.warning(f"Invalid bot spymaster clue '{clue}': {msg}")
            if self.consecutive_errors >= self.MAX_ERRORS:
                self.logger.error("Bot disqualified after 3 invalid clues.")
                self.game.is_victory = False
                self.game.phase = Phase.GAME_OVER
                self.check_game_over()
                return
        self.bot_action_scheduled = False
        self.update_ui()

    def execute_bot_guesser(self):
        obs = self.game.get_observation_for_guesser()
        guess = self.guesser.get_guess(obs)
        if guess.upper() == "PASS":
            self.consecutive_errors = 0
            self.game.end_guessing_early()
            if self.game_logger:
                self.game_logger.log_guess("PASS", "PASS")
        else:
            card_type = next((c.card_type.value for c in self.game.board if c.word == guess), "UNKNOWN")
            success, msg = self.game.guess(guess)
            if success:
                self.consecutive_errors = 0
                self.logger.info(f"Bot Guesser guessed: {guess}")
                if self.game_logger:
                    self.game_logger.log_guess(guess, card_type)
            else:
                self.consecutive_errors +=1
                self.logger.warning(f"Invalid bot guess attempt '{guess}': {msg}")
                if self.consecutive_errors >= self.MAX_ERRORS:
                    self.logger.error("Bot disqualified after 3 invalid guesses.")
                    self.game.is_victory = False
                    self.game.phase = Phase.GAME_OVER
                    self.check_game_over()
                    return
                #TODO niech ui zmienia sie po zaakceptowaniu message boxa
        self.bot_action_scheduled = False
        self.check_game_over()
        self.update_ui()

    def update_ui(self):
        self.score_label.configure(text=f"Remaining targets: {self.game._get_score()}")
        is_spymaster_turn = (self.game.phase == Phase.GIVING_CLUE)
        is_game_over = (self.game.phase == Phase.GAME_OVER)
        human_is_spymaster = (is_spymaster_turn and self.spymaster is None)

        if is_game_over:
            self.info_label.configure(text="GAME OVER")
            self.clue_input_frame.pack_forget()
            self.pass_btn.pack_forget()
        elif is_spymaster_turn:
            self.pass_btn.pack_forget()
            if self.spymaster is None:
                self.info_label.configure(text="SPY MASTER TURN:\nGive a clue.")
                self.clue_input_frame.pack(pady=20)
            else:
                self.info_label.configure(text="Bot Spymaster is thinking...\nPlease wait.")
                self.clue_input_frame.pack_forget()
                if not self.bot_action_scheduled:
                    self.bot_action_scheduled = True
                    self.after(500, self.execute_bot_spymaster)
        else:
            self.clue_input_frame.pack_forget()

            if self.guesser is None:
                self.info_label.configure(
                    text=f"Guessers turn:\nClue: {self.game.current_clue}\nRemaining: {self.game.guesses_allowed - self.game.guesses_made}")
                self.pass_btn.pack(pady=10)
            else:
                self.info_label.configure(text=f"Bot Guesser is thinking...\nClue: {self.game.current_clue}")
                self.pass_btn.pack_forget()
                if not self.bot_action_scheduled:
                    self.bot_action_scheduled = True
                    self.after(1000, self.execute_bot_guesser)
        for card in self.game.board:
            btn = self.buttons[card.word]

            ctype = card.card_type.value
            if ctype == "TARGET":
                card_color = self.COLOR_TARGET
            elif ctype == "NEUTRAL":
                card_color = self.COLOR_NEUTRAL
            else:
                card_color = self.COLOR_ASSASSIN

            if card.is_revealed or human_is_spymaster or is_game_over:
                btn.configure(fg_color=card_color, text_color="black")
                if card.is_revealed:
                    btn.configure(state="disabled", text=f"{card.word}\n[X]")
                else:
                    state = "disabled" if is_game_over else "normal"
                    btn.configure(state=state, text=f"{card.word}\n")
            else:
                btn.configure(fg_color=self.COLOR_UNKNOWN, text_color="white", state="normal", text=f"{card.word}\n")