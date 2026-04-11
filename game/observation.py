from dataclasses import dataclass
from typing import List,Optional


@dataclass
class ObservationCard:
    """
        Represents a single card on the board as seen by a player.
        Parameters:
            word (str): The word of the card.
            type (str): The type of the card.
            revealed (bool): Whether the card is revealed or not.
    """
    word: str
    type: str
    revealed: bool

@dataclass
class SpymasterObservation:
    """
        The full state of the game visible to the Spymaster.
        The Spymaster knows the true identity of all cards.
        Parameters:
            board (List[ObservationCard]): The board state.
            score (int): The current score.
            turn_taken (int): The turn number.
        """
    board: List[ObservationCard]
    score: int
    turn_taken: int

@dataclass
class GuesserObservation:
    """
        The partial state of the game visible to the Guesser.
        The Guesser only knows the types of cards that have been explicitly revealed.
        Parameters:
            clue (Optional[str]): The current clue.
            remaining_guesses (int): The number of remaining guesses.
            board (List[ObservationCard]): The board state.
            score (int): The current score.
        """
    clue: Optional[str]
    remaining_guesses: int
    board: List[ObservationCard]
    score: int
