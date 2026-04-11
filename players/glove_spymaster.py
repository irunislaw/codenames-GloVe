from typing import Dict, Tuple

from game.observation import SpymasterObservation
from players.interfaces.spymaster import SpyMaster


class GloveSpyMaster(SpyMaster):
    def get_clue(self, obs:SpymasterObservation) -> Tuple[str, int]:
        #TODO Implement glove
        #print("Glove bot turn(spymaster)")
        return "ROBOT",2
