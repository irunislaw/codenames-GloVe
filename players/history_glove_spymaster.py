import numpy as np
import time

from players.glove_spymaster import GloveSpyMaster
from game.observation import SpymasterObservation 
from utils.table_recorder import table_recorder

from typing import Dict, Tuple

class HistoryGloveSpyMaster(GloveSpyMaster):
    def __init__(self, **kwargs):
        table_recorder.load_table()
        super().__init__(**kwargs)

    def get_clue(self, obs:SpymasterObservation) -> Tuple[str, int]:
        start_time = time.time()
        time_limit = self.time_limit

        unrevealed_cards = [c for c in obs.board if not c.revealed and c.word.lower() in self.glove] 
        targets = [c.word.lower() for c in unrevealed_cards if c.type == 'TARGET']
        neutrals = [c.word.lower() for c in unrevealed_cards if c.type == 'NEUTRAL']
        assassin = [c.word.lower() for c in unrevealed_cards if c.type == 'ASSASSIN']
        assassin_word = assassin[0].lower() if assassin else None
        assassin_list = [(assassin_word, -self.weight_assassin)]
        neutral_list = [(neutral_word, -self.weight_neutral) for neutral_word in neutrals]
        board_words = {c.word.upper() for c in obs.board}
        targets_left = len(targets)

        number_targets = table_recorder.get_best_target_count(targets_left)     
        print(f"[HISTORY_SPYMASTER] clue_targets: {number_targets}, targets_left: {targets_left}")   
        # check only fixed number of targets
        word_count_list = [number_targets]
        best_clue, best_word_count, best_score, best_selected_targets = self._find_best_clue(
            word_count_list,
            targets,
            assassin_list,
            neutral_list, 
            board_words, 
            time_limit
        )
        if self.logger:
            similarities = []
            if best_clue and best_selected_targets:
                for w in best_selected_targets:
                    try:
                        sim = float(self.glove.similarity(best_clue, w))
                    except Exception:
                        sim = 0.0
                    similarities.append(sim)
            self.logger.log_spymaster_words(best_selected_targets, similarities)
        if self.terminal:
            self.terminal.info(f"targets {targets}")
            self.terminal.info(f"assassin {assassin}")
            self.terminal.info(f"clue {best_clue}")
            self.terminal.info(f"score {best_score}")

        return best_clue, best_word_count