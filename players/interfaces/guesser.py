from abc import ABC, abstractmethod

from game.observation import GuesserObservation
from utils.game_logger import GameLogger


class Guesser(ABC):
    @abstractmethod
    def get_guess(self, obs: GuesserObservation)->str:
        pass