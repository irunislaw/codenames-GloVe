from abc import ABC, abstractmethod
from typing import Tuple

from game.observation import SpymasterObservation


class SpyMaster(ABC):
    @abstractmethod
    def get_clue(self, obs: SpymasterObservation)-> Tuple[str, int]:
        pass