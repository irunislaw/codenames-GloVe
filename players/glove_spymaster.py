from typing import Dict, Tuple

from players.interfaces.spymaster import SpyMaster


class GloveSpyMaster(SpyMaster):
    def get_clue(self, obs:Dict) -> Tuple[str, int]:
        #TODO Implement glove
        #print("Glove bot turn(spymaster)")
        return "ROBOT",2
