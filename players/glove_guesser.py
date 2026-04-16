from typing import Dict
# import random

from game.observation import GuesserObservation
from players.interfaces.guesser import Guesser

import gensim.downloader as api
import itertools


class GloveGuesser(Guesser):
    def __init__(self, model="glove-wiki-gigaword-100"):
        super().__init__()
        # TODO Podmienic inicjalizacje modelu na ta bardziej optymalna
        self.glove = api.load(model)
        self.last_guess = None
        self.current_list = []

    def generate_list(self, possibilities, clue, n):
        best_similarity = -float('inf')
        best_combination = None

        clue_vector = self.glove[clue]

        combinations = [list(c) for c in itertools.combinations(possibilities, n)]

        for comb in combinations:
            comb_vector = self.glove.get_mean_vector(
                keys=comb,
                pre_normalize=True,
                post_normalize=True
            )

            sim = self.glove.cosine_similarities(clue_vector, [comb_vector])[0]

            if sim > best_similarity:
                best_similarity = sim
                best_combination = comb

        # DEBUG
        print(best_combination)
        # print([self.glove.cosine_similarities(clue_vector, [self.glove[x]])[0] for x in possibilities])

        self.current_list = best_combination


    def get_guess(self, obs: GuesserObservation) -> str:
        
        unrevealed = [c.word.lower() for c in obs.board if not c.revealed]
        clue = obs.clue.lower()

        
        if obs.remaining_guesses == 1:
            #TODO Mozna dodac probe odgadniecia dodatkowego hasla
            return "PASS"
        
        
        if self.last_guess is not None:
            last_type = next(card.type for card in obs.board if card.word.lower() == self.last_guess)
        
    
        if not self.current_list or last_type == "NEUTRAL":
            self.generate_list(unrevealed, clue, obs.remaining_guesses - 1)
        
        
        guess = self.current_list.pop(0)
        self.last_guess = guess
        return guess