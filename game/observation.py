from dataclasses import dataclass
from typing import List,Optional


@dataclass
class ObservationCard:
    word: str
    type: str
    revealed: bool

@dataclass
class SpymasterObservation:
    board: List[ObservationCard]
    score: int
    turn_taken: int

@dataclass
class GuesserObservation:
    clue: Optional[str]
    remaining_guesses: int
    board: List[ObservationCard]
    score: int
