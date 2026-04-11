from abc import ABC, abstractmethod
class Guesser(ABC):
    @abstractmethod
    def get_guess(self, obs: dict):
        pass