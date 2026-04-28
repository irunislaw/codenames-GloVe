import logging
import sys
from typing import Dict, Tuple

from game.observation import SpymasterObservation
from players.interfaces.spymaster import SpyMaster

import gensim.downloader as api
import json
import numpy as np

from game.codenames import Codenames
import random
import itertools

from utils.game_logger import GameLogger
from utils.load_model import Model


class GloveSpyMaster(SpyMaster):
    # ONLY 1 TEAM GAMES

    def __init__(self, words_pool_path="data/words.txt", model="glove-wiki-gigaword-100", weight_assasin=0.5, logger: GameLogger = None):
        super().__init__()
        self.terminal = logging.getLogger()
        model_manager = Model()
        self.glove = model_manager.load_model(name = model)
        self.weight_assasin = weight_assasin
        self.logger = None
        if logger:
            self.logger = logger
        self.last_top_k = []
        # oddzielnie czyta słownik z pliku
        WORDS_FILE_PATH = "data/words.txt"
        try:
            with open(WORDS_FILE_PATH, 'r', encoding='utf-8') as f:
                words_pool = [line.strip().upper() for line in f if line.strip()]
        except FileNotFoundError:
            self.terminal.error(f"Error: Couldnt find {WORDS_FILE_PATH}.")
            exit()             
        self.words_pool = words_pool

    def calculate_score(self, clue_vec, targets_vecs, assasin_vec):
        target_sims = self.glove.cosine_similarities(clue_vec, targets_vecs)

        score = np.sum(target_sims)

        if assasin_vec is not None:
            # dot product gives cosine similarity
            assasin_sim = np.dot(clue_vec, assasin_vec)
            score -= assasin_sim
        return score

    def get_clue(self, obs:SpymasterObservation) -> Tuple[str, int]:
        #TODO Żeby przeszukiwał też inne ilości słów do zgadnięcia niż 2
        #tu moze jakos robic wagi według similarity tylko trzeba to wyważyc,
        # chodzi mi o to ze zaczynamy od kombinacji czwórek np.
        # i sprawdzamy similarity i jak jest dos wysokie to mozemy dac to clue, a jak nie to mniej wyrazów jeszcze
        #TODO Żeby działało gdy zostaną mniej niż 2 słowa do zgadnięcia na planszy
        targets = [c.word.lower() for c in obs.board if not c.revealed and c.type == 'TARGET' and c.word.lower() in self.glove]
        assassin = [c.word for c in obs.board if not c.revealed and c.type == 'ASSASSIN' and c.word.lower() in self.glove]
        assassin_word = assassin[0].lower() if assassin else None
        word_count = 2  # HARDCODED
        if len(targets) == 1:
            word_count = 1


        # get all combinations of the target words
        target_combinations = itertools.combinations(targets, word_count)

        best_clue = None
        best_score = -float('inf')
        best_selected_targets = None

        board_words = {c.word.upper() for c in obs.board}
        all_candidates = []
        for selected_targets in target_combinations:
            selected_targets_list = list(selected_targets)
            assassin_list = [(assassin_word, -self.weight_assasin)]
            try:

                similar_words = self.glove.most_similar(
                    positive=selected_targets_list,
                    negative=assassin_list,
                    topn=15,
                )
            except Exception:
                continue
            for current_clue, current_score in similar_words:
                if current_clue.upper() in board_words:
                    print(f"Skipping {current_clue} because it's already revealed")
                    continue
                all_candidates.append({
                    "clue": current_clue,
                    "score": current_score,
                    "targets": selected_targets_list,
                    "count": word_count
                })
        if not all_candidates:
            self.last_top_k = []
            return "PASS", 0
        all_candidates.sort(key=lambda x: x["score"], reverse=True)

        best_candidate = all_candidates[0]
        best_clue = best_candidate["clue"]
        best_score = best_candidate["score"]
        best_selected_targets = best_candidate["targets"]
        best_word_count = best_candidate["count"]

        self.last_top_k = [{"clue": c["clue"], "score": c["score"]} for c in all_candidates[:5]]

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

        return best_clue,best_word_count

def quick_test(name="glove-wiki-gigaword-300"):
    model_manager = Model()
    model = model_manager.load_model(name)
    # Quick test: Find a clue for 'Apple' and 'Washington'
    print(model.most_similar(positive=['epstein'], topn=10))

def model_info(name="glove-wiki-gigaword-300"):
    print(list(api.info()['models'].keys()))
    info = api.info(name)
    print(json.dumps(info, indent=4))
    print(api.load(name, return_path=True))

if __name__=="__main__":
    # test glove embeddings
    #TODO USUNIECIE ZEBY DAWALO HASLA Z LICZBAMI ALBO -
    logging.basicConfig(level=logging.NOTSET, format='%(message)s', stream=sys.stdout)
    quick_test()
    # WORDS_FILE_PATH = "data/words.txt"
    # try:
    #     with open(WORDS_FILE_PATH, 'r', encoding='utf-8') as f:
    #         words_pool = [line.strip().upper() for line in f if line.strip()]
    # except FileNotFoundError:
    #     print(f"Error: Couldnt find {WORDS_FILE_PATH}.")
    #     exit()
    # game = Codenames(words=random.sample(words_pool, 25))
    # obs = game.get_observation_for_spymaster()
    #
    # agent = GloveSpyMaster()
    #
    # agent.get_clue(obs)
