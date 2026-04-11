from abc import ABC, abstractmethod
class SpyMaster(ABC):
    @abstractmethod
    def get_clue(self, obs: dict):
        pass