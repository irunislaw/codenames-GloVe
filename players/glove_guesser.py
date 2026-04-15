from typing import Dict
import random

from game.observation import SpymasterObservation, GuesserObservation
from players.interfaces.guesser import Guesser


class GloveGuesser(Guesser):
    #TODO implement
    def get_guess(self, obs: GuesserObservation, logger= None) -> str:
        #print("Glove bot turn(guesser)")

        unrevealed = [c.word for c in obs.board if not c.revealed]
        return random.choice(unrevealed) if unrevealed else "PASS"