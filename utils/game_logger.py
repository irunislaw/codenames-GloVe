import csv
import gzip
import os
import pickle
from datetime import datetime

from game.codenames import Codenames



class GameLogger:
    def __init__(self, spymaster_name: str, guesser_name: str, board_id: str = "random"):
        self.game_id = datetime.now().strftime("%Y%m%d-%H%M%S_%f")
        self.board_id = board_id
        self._pending_words = None
        self._pending_similarities = None
        self.stats = {
            "game_id": self.game_id,
            "board_id": self.board_id,
            "spymaster": spymaster_name,
            "guesser": guesser_name,
            "is_victory": False,
            "turns_taken": 0,
            "total_guesses_made": 0,
            "neutral_hits": 0,
            "assassin_hit": False,
            "targets_left": 9,
            "clues_history": [],
            "spymasters_words": [],
            "disqualified": False,
            "disqualification_reason": ""
        }
        self.binary_history = []
        self.initial_board = []

    def log_invalid_action(self, action_type: str, attempt: str, reason: str):
        self.binary_history.append({
            "action": f"INVALID_{action_type}",
            "attempt": attempt,
            "reason": reason
        })

    def set_disqualified(self, reason: str):
        self.stats["disqualified"] = True
        self.stats["disqualification_reason"] = reason
        self.binary_history.append({"action": "DISQUALIFIED", "reason": reason})

    def set_initial_board(self, board):
        self.initial_board = [(c.word, c.card_type.value) for c in board]

    def log_clue(self, clue: str, count: int, latency: float = 0.0, score_left: int = 9, top_k: list = None):
        self.stats["clues_history"].append(clue)

        event = {
            "action": "CLUE",
            "clue": clue,
            "count": count,
            "latency": latency,
            "score_left": score_left
        }
        if top_k:
            event["top_k"] = top_k

        if hasattr(self, '_pending_words') and self._pending_words is not None:
            event["words"] = self._pending_words
            self._pending_words = None
        if hasattr(self, '_pending_similarities') and self._pending_similarities is not None:
            event["similarities"] = self._pending_similarities
            self._pending_similarities = None
        self.binary_history.append(event)

    def log_spymaster_words(self, words: list, similarities: list = None):
        #self.stats["spymasters_words"].append(words)
        self._pending_words = words
        self._pending_similarities = similarities

    def log_guess(self, word: str, result_type: str, latency: float = 0.0, score_left: int = 9):
        self.stats["total_guesses_made"] += 1
        self.binary_history.append({
            "action": "GUESS",
            "word": word,
            "result": result_type,
            "latency": latency,
            "score_left": score_left
        })

        if result_type == "NEUTRAL":
            self.stats["neutral_hits"] += 1
        elif result_type == "ASSASSIN":
            self.stats["assassin_hit"] = True


    def finalize_game(self, game: Codenames):
        self.stats["is_victory"] = game.is_victory
        self.stats["turns_taken"] = game.turn_taken
        self.stats["targets_left"] = game.get_score()

    def save_stats_to_csv(self, filepath: str):
        os.makedirs(os.path.dirname(filepath),exist_ok=True)
        file_exists = os.path.isfile(filepath)

        row_to_save = self.stats.copy()
        row_to_save["clues_history"] = "|".join(row_to_save["clues_history"])

        with open(filepath, "a", newline='',encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=row_to_save.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(row_to_save)

    def save_binary_replay(self, folderpath: str, custom_filename: str = None):
        os.makedirs(folderpath,exist_ok=True)
        filename_str = custom_filename if custom_filename else f"replay_{self.game_id}.pkl.gz"
        filename = os.path.join(folderpath, filename_str)

        data = {
            "game_id": self.game_id,
            "board_id": self.board_id,
            "initial_board": self.initial_board,
            "history": self.binary_history
        }
        with gzip.open(filename, "wb") as f:
            pickle.dump(data, f)
