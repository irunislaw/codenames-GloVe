from abc import ABC, abstractmethod

from game.observation import GuesserObservation


class Guesser(ABC):
    @abstractmethod
    def get_guess(self, obs: GuesserObservation)->str:
        pass