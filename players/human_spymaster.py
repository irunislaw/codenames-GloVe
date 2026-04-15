from typing import Dict, Tuple

from players.interfaces.spymaster import SpyMaster


class HumanSpyMaster(SpyMaster):
    def get_clue(self, obs: Dict, logger= None) -> Tuple[str, int]:
        print("\n==== Your turn(Spymaster) ====")
        clue = input("Enter your clue: ").strip()
        while True:
            try:
                count = int(input("Enter the number of guesses allowed: "))
                return clue, count
            except ValueError:
                print("Invalid input. Please enter a valid number.")