from typing import List

from game.codenames import Codenames, Phase
from players.interfaces.guesser import Guesser
from players.interfaces.spymaster import SpyMaster


class GameRunner:
    C_GREEN = '\033[92m'
    C_RED = '\033[91m'
    C_GRAY = '\033[90m'
    C_WHITE = '\033[97m'
    C_RESET = '\033[0m'
    C_BG_REVEALED = '\033[40m'

    def __init__(self, spymaster: SpyMaster,guesser: Guesser, words: List[str], render: bool = True):
        self.game = Codenames(words)
        self.spymaster = spymaster
        self.guesser = guesser
        self.render = render
    #TODO zamienic DICT na cos innego zeby ide podpowiadalo klucze
    def _draw_board(self, observation: dict, is_spymaster: bool):
        if not self.render:
            return
        print("\n" + "="*60)
        print(" PLANSZA ".center(60, "="))
        print("=" * 60)
        board = observation["board"]
        for i in range(0, 25, 5):
            row = board[i:i + 5]
            row_str = ""
            for card in row:
                word = card["word"].center(11)
                ctype = card["type"]
                revealed = card["revealed"]
                color = self.C_WHITE
                bg = self.C_BG_REVEALED if revealed else ""
                if ctype == "TARGET": color = self.C_GREEN
                elif ctype == "NEUTRAL": color = self.C_GRAY
                elif ctype == "ASSASIN": color = self.C_RED
                elif ctype == "UNKNOWN": color = self.C_WHITE

                marker = "[X]" if revealed else "   "
                if revealed and not is_spymaster:
                    if card["type"] == "TARGET": color = self.C_GREEN
                    elif card["type"] == "ASSASIN": color = self.C_RED
                    else: color = self.C_GRAY
                row_str += f"{color}{bg}{marker}{word}{self.C_RESET} | "
            print(row_str)
        print("=" * 60)

    def run(self):
        while self.game.phase != Phase.GAME_OVER:
            if self.game.phase == Phase.GIVING_CLUE:
                obs = self.game.get_observation_for_spymaster()
                if self.render:
                    self._draw_board(obs, True)
                clue, count = self.spymaster.get_clue(obs)
                self.game.give_clue(clue, count)
            elif self.game.phase == Phase.GUESSING:
                obs = self.game.get_observation_for_guesser()
                if self.render:
                    self._draw_board(obs, False)
                guess = self.guesser.get_guess(obs)
                if guess.upper() == "PASS":
                    self.game.end_guessing_early()
                    print("Passing turn...")
                else:
                    success, message = self.game.guess(guess)
                    if not success:
                        print(f"Error: {message}")
                    else:
                        print(f"Guess: {guess} - {message}")
        print(f"Game over!")
        if self.game.is_victory:
            print(f"You won in {self.game.turn_taken} turns!")
        else:
            print(f"You lost in {self.game.turn_taken} turns!")
