import numpy as np
import os

from enum import Enum
from game.observation import SpymasterObservation

from config import settings

PRINT_LOGS = True

class State(Enum):
    GIVING_CLUE="GIVING_CLUE"
    GUESSING="GUESSING"

# To jest klasa do zapisywania sobie ile targetów daje ile zgadnięć
class TableRecorder():
    def __init__(self, table_path="data/table.npy", save_freq=5):
        self.table = np.zeros(shape=(10, 10, 10))
        self.table_path = table_path
        self.state = State.GIVING_CLUE
        self.clue_targets = None
        self.guessed_words = None
        self.targets_left = None
        self.counter = 1
        self.save_freq = save_freq
    
    def load_table(self):
        try:
            loaded_array = np.load(self.table_path)
        except Exception as e:
            loaded_array = np.zeros(shape=(10,10,10), dtype=int)
        self.table = loaded_array

    def save_table(self):
        file_dir = os.path.dirname(self.table_path)
        if file_dir and not os.path.exists(file_dir):
            os.makedirs(file_dir, exist_ok=True)
        if PRINT_LOGS:
            print("[Table Recorder]: saved table")
        np.save(self.table_path, self.table)

    def record_obs(self, obs: SpymasterObservation, clue_targets):
        if self.state != State.GIVING_CLUE:
            if PRINT_LOGS:
                print("[Table Recorder]: not expecting to record a clue")
            return
        unrevealed_cards = [c for c in obs.board if not c.revealed] 
        targets = [c.word.lower() for c in unrevealed_cards if c.type == 'TARGET']
        targets_left = len(targets)
        if PRINT_LOGS:
            print("[Table Recorder]: recorded [clue_targets:", clue_targets, "targets_left:", targets_left, "]")
        self.guessed_words=0
        self.state = State.GUESSING
        self.clue_targets = clue_targets 
        self.targets_left = targets_left

    def record_guess(self, target_hit):
        if self.state != State.GUESSING:
            if PRINT_LOGS:
                print("[Table Recorder]: not expecting guessing")
            return
        if target_hit:
            self.guessed_words+=1

    def record_end_turn(self):
        if self.state != State.GUESSING:
            if PRINT_LOGS:            
                print("[Table Recorder]: not expecting end of turn")
            return
        if self.clue_targets == None:
            if PRINT_LOGS:            
                print("[Table Recorder]: missing target count information")
            return
        if self.targets_left == None:
            if PRINT_LOGS:            
                print("[Table Recorder]: missing targets left information")
            return
        
        if PRINT_LOGS:            
            print("[Table Recorder]: recorded end of turn", self.counter)
        self.state = State.GIVING_CLUE
        self.table[self.clue_targets][self.guessed_words][self.targets_left]+=1
        if self.counter % self.save_freq == 0:
            self.counter = 1
            self.save_table()
            self.guessed_words = 0
            return
        self.counter+=1
        
    def print_table(self):
        print(self.table)

    def print_statistics(self):
        """
        Calculates and prints game statistics compiled from the 3D numpy table.
        Dimensions: [clue_targets][guessed_words][targets_left]
        """
        print("\n" + "="*105)
        print(f"{'CODENAMES GAME STATISTICS':^105}")
        print("="*105)
        
        # Table Header Configuration
        header_format = "{:<14} | {:<12} | {:<20} | {:<22} | {:<24}"
        row_format = "{:<14} | {:<12} | {:<20} | {:<22.2f} | {:<24.2f}"
        
        print(header_format.format(
            "Clue Targets", 
            "Total Turns", 
            "Total Guessed Words", 
            "Avg Guessed Words", 
            "Avg Targets Left"
        ))
        print("-" * 105)

        for clue_target in range(1, self.table.shape[0]):
            slice_2d = self.table[clue_target]
            total_turns = np.sum(slice_2d)

            if total_turns == 0:
                continue # Skip rendering rows with no data

            guessed_word_counts = np.sum(slice_2d, axis=1) 
            total_guessed_words = np.sum(guessed_word_counts * np.arange(self.table.shape[1]))
            avg_guessed = total_guessed_words / total_turns

            targets_left_counts = np.sum(slice_2d, axis=0) 
            total_targets_left = np.sum(targets_left_counts * np.arange(self.table.shape[2]))
            avg_targets_left = total_targets_left / total_turns

            print(row_format.format(
                clue_target, 
                int(total_turns), 
                int(total_guessed_words), 
                avg_guessed, 
                avg_targets_left
            ))
            
        print("="*105 + "\n")

    def calculate_expected_guessed_words(self, targets_left_query):
        matrix2d = self.table[:,:,targets_left_query]
        total_turns = np.sum(matrix2d, axis=1)
        # np.arange(10) creates the multipliers [0, 1, 2...9] for the guessed_words dimension
        weighted_guesses = np.sum(matrix2d * np.arange(self.table.shape[1]), axis=1)

        expected_guesses = np.divide(weighted_guesses, total_turns, out=np.zeros_like(weighted_guesses, dtype=float), where=total_turns!=0)
        return expected_guesses

    def get_best_target_count(self, targets_left_query):
        expected_guesses = self.calculate_expected_guessed_words(targets_left_query)
        return np.argmax(expected_guesses).item()

table_recorder = TableRecorder()
if settings["game"]["record_table"]:
    table_recorder.load_table()

if __name__=="__main__":
    table_recorder.load_table()
    table_recorder.print_statistics()
    print(table_recorder.get_best_target_count(5))