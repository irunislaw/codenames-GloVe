from typing import Dict, Tuple

from game.observation import SpymasterObservation
from players.interfaces.spymaster import SpyMaster

import gensim.downloader as api
import json
import numpy as np

from game.codenames import Codenames
import random
import itertools


class GloveSpyMaster(SpyMaster):
    # ONLY 1 TEAM GAMES

    def __init__(self, words_pool_path="data/words.txt", model="glove-wiki-gigaword-100", weight_assasin=0.5):
        super().__init__()
        # każdy agent wczytuje model oddzielnie
        # możliwe, że to jest nieoptymalne
        print("loading glove model")
        glove = api.load(model)
        print("loading finished")
        self.glove = glove # glove behaves like a list
        self.weight_assasin = weight_assasin
        # oddzielnie czyta słownik z pliku
        WORDS_FILE_PATH = "data/words.txt"
        try:
            with open(WORDS_FILE_PATH, 'r', encoding='utf-8') as f:
                words_pool = [line.strip().upper() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Error: Couldnt find {WORDS_FILE_PATH}.")
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
        #TODO Żeby działało gdy zostaną mniej niż 2 słowa do zgadnięcia na planszy
        targets = [c.word.lower() for c in obs.board if not c.revealed and c.type == 'TARGET' and c.word.lower() in self.glove]
        assassin = [c.word for c in obs.board if not c.revealed and c.type == 'ASSASSIN' and c.word.lower() in self.glove]
        assassin_word = assassin[0].lower() if assassin else None
        
        word_count = 2 # HARDCODED

        # get all combinations of the target words
        target_combinations = itertools.combinations(targets, word_count)

        best_clue = None
        best_score = -float('inf')

        for selected_targets in target_combinations:
            selected_targets_list = list(selected_targets)
            assassin_list = [(assassin_word, -self.weight_assasin)]
            current_clue, current_score = self.glove.most_similar(
                positive=selected_targets_list, 
                negative=assassin_list,
                topn=1,
            )[0]
            board_words = {c.word.upper() for c in obs.board}
            if current_clue.upper() in board_words:
                continue

            if current_score > best_score:
                best_clue = current_clue
                best_score = current_score

        #print("Glove bot turn(spymaster)")
        print("targets", targets)
        print("assasin", assassin)
        print("clue", best_clue)
        print("score", best_score)
        return best_clue,word_count

def quick_test(name="glove-wiki-gigaword-300"):
    model = api.load(name)
    # Quick test: Find a clue for 'Apple' and 'Washington'
    print(model.most_similar(positive=['apple', 'washington'], topn=5))

def model_info(name="glove-wiki-gigaword-300"):
    print(list(api.info()['models'].keys()))
    info = api.info(name)
    print(json.dumps(info, indent=4))
    print(api.load(name, return_path=True))

if __name__=="__main__":
    # test glove embeddings
    WORDS_FILE_PATH = "data/words.txt"
    try:
        with open(WORDS_FILE_PATH, 'r', encoding='utf-8') as f:
            words_pool = [line.strip().upper() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: Couldnt find {WORDS_FILE_PATH}.")
        exit()            
    game = Codenames(words=random.sample(words_pool, 25))
    obs = game.get_observation_for_spymaster()

    agent = GloveSpyMaster()

    agent.get_clue(obs)
