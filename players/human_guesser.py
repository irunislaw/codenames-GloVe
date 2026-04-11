from typing import Dict

from players.interfaces.guesser import Guesser


class HumanGuesser(Guesser):
    def get_guess(self, obs: Dict):
        print("\n==== Your turn(Guesser) ====")
        print(f"Clue: '{obs['clue']}'. Remaining guesses: {obs['remaining_guesses']}")
        return input("Enter your guess (enter 'PASS' to end your turn):").strip()