import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple
import copy

from game.observation import SpymasterObservation, ObservationCard, GuesserObservation


class CardType(Enum):
    TARGET = "TARGET"
    NEUTRAL = "NEUTRAL"
    ASSASSIN = "ASSASSIN"

class Phase(Enum):
    GIVING_CLUE = "GIVING_CLUE"
    GUESSING = "GUESSING"
    GAME_OVER = "GAME_OVER"

@dataclass
class Card:
    word: str
    card_type: CardType
    is_revealed: bool = False    

class Codenames:
    
    def __init__(self, words: Optional[List[str]] = None, pregenerated_board: Optional[List[Card]] = None , target_count: int = 9):
        if pregenerated_board:
            self.board = copy.deepcopy(pregenerated_board)
        elif words and len(words) == 25:
            self.board = self._generate_board(words,target_count)
        else:
            raise ValueError("Board has to contain exactly 25 words or pregenerated_board must be provided")
        self.phase: Phase = Phase.GIVING_CLUE
        self.is_victory: Optional[bool] = None
        self.turn_taken: int = 0
        self.current_clue: Optional[str] = None
        self.guesses_allowed: int = 0
        self.guesses_made: int = 0

    def _generate_board(self, words: List[str], target_count: int) -> List[Card]:
        neutral_count = 25 - target_count - 1

        types = [CardType.TARGET] * target_count + \
                [CardType.NEUTRAL] * neutral_count + \
                [CardType.ASSASSIN] * 1
        random.shuffle(types)
        return [Card(word=w,card_type=t) for w,t in zip(words,types)]

    def get_observation_for_spymaster(self)-> SpymasterObservation:
        board_obs = [ObservationCard(word=c.word, type=c.card_type.value, revealed=c.is_revealed) for c in self.board]
        return SpymasterObservation(
            board=board_obs,
            score=self._get_score(),
            turn_taken=self.turn_taken
        )
    def get_observation_for_guesser(self)-> GuesserObservation:
        visible_board = []
        for c in self.board:
            visible_board.append(ObservationCard(
                word= c.word,
                type= c.card_type.value if c.is_revealed else "UNKNOWN",
                revealed= c.is_revealed
            ))
        return GuesserObservation(
            clue= self.current_clue,
            remaining_guesses= self.guesses_allowed - self.guesses_made,
            board= visible_board,
            score= self._get_score()
        )
    def give_clue(self, clue: str, count: int) -> bool:
        if self.phase != Phase.GIVING_CLUE:
            return False
        self.current_clue = clue
        self.guesses_allowed = count + 1
        self.guesses_made = 0
        self.phase = Phase.GUESSING
        self.turn_taken += 1
        return True

    def guess(self, word: str) -> Tuple[bool, str]:
        if self.phase != Phase.GUESSING:
            return False, "Not in guessing phase"
        card = next((c for c in self.board if c.word == word), None)

        if not card or card.is_revealed:
            return False, "Word not found or already revealed"

        card.is_revealed = True
        self.guesses_made += 1

        if card.card_type == CardType.ASSASSIN:
            self.is_victory = False
            self.phase = Phase.GAME_OVER
            return True, "Game over, you lost"
        elif card.card_type == CardType.NEUTRAL:
            self._end_turn()
            return True, "Miss, end of turn"
        else:
            if self._check_win_condition():
                return True, "Game over, you won!"
            if self.guesses_made >= self.guesses_allowed:
                self._end_turn()
                return True, "End of moves"
            return True, "Hit, keep guessing"

    def end_guessing_early(self)-> bool:
        if self.phase != Phase.GUESSING:
            return False
        self._end_turn()
        return True

    def _end_turn(self):
        self.phase = Phase.GIVING_CLUE
        self.current_clue = None
        self.guesses_allowed = 0
        self.guesses_made = 0

    def _check_win_condition(self)-> bool:
        if self._get_score ==0:
            self.is_victory = True
            self.phase = Phase.GAME_OVER
            return True
        return False

    def _get_score(self)-> int:
        return sum(1 for c in self.board if c.card_type == CardType.TARGET and not c.is_revealed)

