from game.game_runner import GameRunner
from players.glove_guesser import GloveGuesser
from players.glove_spymaster import GloveSpyMaster
from players.human_guesser import HumanGuesser
from players.human_spymaster import HumanSpyMaster

if __name__ == "__main__":
    words_pool = [
        "DOG", "CAT", "HOUSE", "CAR", "TREE", "RIVER", "MOUNTAIN", "BRIDGE", "EYE",
        "CASTLE", "COW", "SPACE", "MOON", "SUN", "PAPER", "KEY",
        "WATER", "FIRE", "WIND", "EARTH", "GOLD", "SILVER", "SWORD", "SHIELD", "HELMET"
    ] #todo lista wiecej slow z bazy

    print("Choose game mode:")
    print("1: Human (Spymaster) vs Human (Guesser)")
    print("2: Human (Spymaster) vs Bot (Guesser)")
    print("3: Bot (Spymaster) vs Human (Guesser)")
    print("4: Bot (Spymaster) vs Bot (Guesser)")
    choice = input("Choice (1-4):")
    spymaster = GloveSpyMaster()
    guesser = GloveGuesser()
    if choice == '1':
        spymaster = HumanSpyMaster()
        guesser = HumanGuesser()
    elif choice == '2':
        spymaster = HumanSpyMaster()
    elif choice == '3':
        guesser = HumanGuesser()

    render_input = input("Render input? (y/n):").strip().upper()
    render = render_input != 'N'

    runner = GameRunner(spymaster, guesser, words_pool, render)
    runner.run()