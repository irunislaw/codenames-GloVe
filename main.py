import gzip
import logging
import os
import pickle
import random

from game.codenames import Codenames
from game.game_runner import GameRunner
from players.glove_guesser import GloveGuesser
from players.glove_spymaster import GloveSpyMaster
from players.human_guesser import HumanGuesser
from players.human_spymaster import HumanSpyMaster
from utils.dataset_manager import DatasetManager
from utils.game_logger import GameLogger

logging.basicConfig(level=logging.INFO, format='%(message)s')
#logging.getLogger().setLevel(logging.WARNING) #odkomentowac gdy chcemy wyciszyc konsole

def select_agents():
    print("\n--- Select Spymaster ---")
    print("1: Human")
    print("2: Glove Bot")
    sm_choice = input("Choice: ").strip()
    spymaster = HumanSpyMaster() if sm_choice == '1' else GloveSpyMaster()

    print("\n--- Select Guesser ---")
    print("1: Human")
    print("2: Glove Bot")
    g_choice = input("Choice: ").strip()
    guesser = HumanGuesser() if g_choice == '1' else GloveGuesser()

    return spymaster, guesser

if __name__ == "__main__":
    WORDS_FILE_PATH = "data/words.txt"
    try:
        with open(WORDS_FILE_PATH, 'r', encoding='utf-8') as f:
            # Odczytuje linie, usuwa białe znaki i zamienia na wielkie litery
            words_pool = [line.strip().upper() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: Couldnt find {WORDS_FILE_PATH}.")
        exit()

    if len(words_pool) < 25:
        print("Error: Not enough words in the word list.")
        exit()

    DATASET_PATH = "data/boards_dataset.json"
    STATS_BASE_DIR = "stats"

    print("\n=== CODENAMES TEST SYSTEM ===")
    print("1. Generate a fixed dataset of 100 boards")
    print("2. Play a single game (Completely random board)")
    print("3. Play a single game (Random board from the dataset)")
    print("4. BATCH EVALUATION: Run bots on all boards in the dataset")
    print("5. WATCH REPLAY: Load and view a saved game")

    choice = input("Select an option (1-5): ").strip()

    if choice == '1':
        if os.path.exists(DATASET_PATH):
            confirm = input(
                f"Dataset already exists at '{DATASET_PATH}'. ARE YOU SURE YOU WANT TO OVERWRITE THE EXISTING DATASET? SPELL 'CONFIRM' to confirm: ").strip().upper()
            if confirm != 'CONFIRM':
                print("Operation cancelled.")
                exit()
        DatasetManager.generate_and_save_dataset(words_pool, 100, DATASET_PATH)

    elif choice in ['2', '3']:
        spymaster, guesser = select_agents()

        if choice == '3':
            if not os.path.exists(DATASET_PATH):
                print(f"Error: Dataset not found at {DATASET_PATH}. Run option 1 first.")
                exit()
            boards = DatasetManager.load_dataset(DATASET_PATH)
            board_id, board = random.choice(boards)
            game = Codenames(pregenerated_board=board)
        else:
            board_id = "random_generation"
            game = Codenames(words=words_pool)

        eval_logger = GameLogger(spymaster.__class__.__name__, guesser.__class__.__name__, board_id=board_id)
        runner = GameRunner(spymaster, guesser, game, render=True, game_logger=eval_logger)
        runner.run()

        single_csv = os.path.join(STATS_BASE_DIR, "single_games", "single_games.csv")
        single_replay_dir = os.path.join(STATS_BASE_DIR, "single_games", "replays")

        eval_logger.save_stats_to_csv(single_csv)
        eval_logger.save_binary_replay(single_replay_dir)
        print(f"\n[!] Stats saved to {single_csv} and binary replay saved to {single_replay_dir}.")

    elif choice == '4':
        if not os.path.exists(DATASET_PATH):
            print(f"Error: Dataset not found at {DATASET_PATH}. Run option 1 first.")
            exit()

        run_name = input("Enter a name for this test run (e.g., test_glove_v1): ").strip()
        if not run_name:
            print("Run name cannot be empty!")
            exit()

        run_dir = os.path.join(STATS_BASE_DIR, run_name)
        csv_path = os.path.join(run_dir, "batch_evaluation.csv")
        replays_dir = os.path.join(run_dir, "replays")

        boards = DatasetManager.load_dataset(DATASET_PATH)
        print(f"Starting evaluation on {len(boards)} boards. This might take a while...")


        logging.getLogger().setLevel(logging.WARNING)

        for board_id, board in boards:
            game = Codenames(pregenerated_board=board)
            spymaster = GloveSpyMaster()
            guesser = GloveGuesser()

            eval_logger = GameLogger(spymaster.__class__.__name__, guesser.__class__.__name__, board_id=board_id)
            runner = GameRunner(spymaster, guesser, game, render=False, game_logger=eval_logger)
            runner.run()

            eval_logger.save_stats_to_csv(csv_path)


            game_number = int(board_id) + 1
            eval_logger.save_binary_replay(replays_dir, custom_filename=f"replay_game_{game_number}.pkl.gz")


        logging.getLogger().setLevel(logging.INFO)
        print(f"\n[Success] Evaluation complete! Data saved to directory: {run_dir}/")

    elif choice == '5':
        if not os.path.exists(STATS_BASE_DIR):
            print("No stats folder found. Run an evaluation first.")
            exit()


        runs = [d for d in os.listdir(STATS_BASE_DIR) if os.path.isdir(os.path.join(STATS_BASE_DIR, d))]

        print("\nAvailable test runs:")
        for r in runs:
            print(f"- {r}")

        selected_run = input("Enter the folder name: ").strip()
        replays_dir = os.path.join(STATS_BASE_DIR, selected_run, "replays")

        if selected_run == "single_games":
            files = [f for f in os.listdir(replays_dir) if f.endswith(".pkl.gz")]
            print("\nAvailable single game replays:")
            for i, f in enumerate(files, 1):
                print(f"{i}: {f}")
            f_idx = int(input("Select file number: ")) - 1
            replay_file = os.path.join(replays_dir, files[f_idx])
        else:
            game_num = input("Enter game number (1-100): ").strip()
            replay_file = os.path.join(replays_dir, f"replay_game_{game_num}.pkl.gz")

        if not os.path.exists(replay_file):
            print("Replay not found.")
            exit()

        with gzip.open(replay_file, "rb") as f:
            data = pickle.load(f)

        print("\n" + "=" * 50 + f"\n REPLAY: {replay_file}\n" + "=" * 50)
        print("\n--- INITIAL BOARD ---")
        for i in range(0, 25, 5):
            print(" | ".join([f"{w}({t})"[:15].ljust(15) for w, t in data["initial_board"][i:i + 5]]))

        print("\n--- HISTORY ---")
        for m in data["history"]:
            if m["action"] == "CLUE":
                print(f"CLUE: '{m['clue']}' ({m['count']})")
            else:
                print(f"GUESS: '{m['word']}' -> {m['result']}")