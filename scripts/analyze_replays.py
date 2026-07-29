import os
import gzip
import pickle
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import shutil


class ReplayAnalyzer:
    def __init__(self, test_name: str):
        self.replays_data = []
        replays_path= os.path.join("stats", test_name, "replays")
        csv_path = os.path.join("stats", test_name, "batch_evaluation.csv")
        self.replays_folder = replays_path
        self.csv_folder = csv_path
        self._load_all_replays()

    def _load_all_replays(self):
        """Loads all replay files from the given folder."""
        search_pattern = os.path.join(self.replays_folder, "*.pkl.gz")
        files = glob.glob(search_pattern)
        print(f"Found {len(files)} replay files in {self.replays_folder}.")

        for file in files:
            try:
                with gzip.open(file, "rb") as f:
                    data = pickle.load(f)
                    self.replays_data.append(data)
            except Exception as e:
                print(f"Error while loading {file}: {e}")


    def get_spymaster_stats(self):
        print("\n--- [B] Statystyki Spymastera ---")
        total_clues = 0
        total_clue_count_sum = 0
        invalid_clues = 0
        similarities_list = []

        for game in self.replays_data:
            for event in game.get("history", []):
                if event.get("action") == "CLUE":
                    total_clues += 1
                    total_clue_count_sum += event.get("count", 0)

                    if "similarities" in event and event["similarities"]:
                        similarities_list.extend(event["similarities"])

                elif event.get("action") == "INVALID_CLUE":
                    invalid_clues += 1

        avg_count = total_clue_count_sum / total_clues if total_clues > 0 else 0
        avg_sim = sum(similarities_list) / len(similarities_list) if similarities_list else 0

        print(f"Number of valid clues: {total_clues}")
        print(f"Average number of words per clue (aggressiveness): {avg_count:.2f}")
        print(f"Invalid clue count (INVALID_CLUE): {invalid_clues}")
        if similarities_list:
            print(f"Average clue similarity (Cosine Similarity): {avg_sim:.4f}")

        return {
            "avg_count": avg_count,
            "invalid_clues": invalid_clues,
            "avg_similarity": avg_sim
        }


    def get_guesser_stats(self):
        print("\n--- [C] Statystyki Guessera ---")
        total_guesses = 0
        correct_guesses = 0
        neutral_hits = 0
        assassin_hits = 0
        passes = 0
        invalid_guesses = 0

        for game in self.replays_data:
            for event in game.get("history", []):
                if event.get("action") == "GUESS":
                    word = event.get("word", "")
                    if word.upper() == "PASS":
                        passes += 1
                    else:
                        total_guesses += 1
                        result = event.get("result", "")
                        if result == "TARGET":
                            correct_guesses += 1
                        elif result == "NEUTRAL":
                            neutral_hits += 1
                        elif result == "ASSASSIN":
                            assassin_hits += 1
                elif event.get("action") == "INVALID_GUESS":
                    invalid_guesses += 1

        precision = (correct_guesses / total_guesses * 100) if total_guesses > 0 else 0

        print(f"Total guess attempts (excluding PASS): {total_guesses}")
        print(f"Accuracy (Hits on TARGET): {precision:.2f}%")
        print(f"Number of passes (PASS): {passes}")
        print(f"Hits on NEUTRAL cards: {neutral_hits}")
        print(f"Hits on ASSASSIN: {assassin_hits}")
        print(f"Illegal guesses (INVALID_GUESS): {invalid_guesses}")

        return {
            "precision": precision,
            "passes": passes,
            "neutral_hits": neutral_hits,
            "assassin_hits": assassin_hits,
            "invalid_guesses": invalid_guesses
        }
    
    def get_game_stats(self):
        print("\n--- [A] Game Statistics ---")

        df = pd.read_csv(self.csv_folder)
        won_games = df['is_victory'].sum()
        total_turns = df['turns_taken'].sum()
        games_total = len(df)
        winrate = won_games / games_total
        avg_turns = total_turns / games_total
        print(f"Win percentage: {winrate * 100}%")
        print(f"Average number of turns: {avg_turns}")


    def generate_charts(self, save_dir="plots"):
        os.makedirs(save_dir, exist_ok=True)
        print(f"\n--- [D] Generating charts for folder: {save_dir} ---")

        game_lengths = []
        mistakes = {"NEUTRAL": 0, "ASSASSIN": 0, "INVALID": 0}
        hits_per_turn = []

        for game in self.replays_data:
            turns = 0
            current_turn_hits = 0

            for event in game.get("history", []):
                if event.get("action") == "CLUE":
                    if turns > 0:
                        hits_per_turn.append((turns, current_turn_hits))
                    turns += 1
                    current_turn_hits = 0

                elif event.get("action") == "GUESS":
                    res = event.get("result", "")
                    if res == "TARGET":
                        current_turn_hits += 1
                    elif res == "NEUTRAL":
                        mistakes["NEUTRAL"] += 1
                    elif res == "ASSASSIN":
                        mistakes["ASSASSIN"] += 1

                elif event.get("action") == "INVALID_GUESS":
                    mistakes["INVALID"] += 1

            if turns > 0:
                hits_per_turn.append((turns, current_turn_hits))
            game_lengths.append(turns)

        if game_lengths:
            plt.figure(figsize=(8, 5))
            sns.histplot(game_lengths, bins=range(1, max(game_lengths) + 2), discrete=True, color='skyblue')
            plt.title("Game Length Distribution (Number of Turns)")
            plt.xlabel("Number of Turns")
            plt.ylabel("Number of Games")
            plt.savefig(os.path.join(save_dir, "game_length_histogram.png"))
            plt.close()

        if sum(mistakes.values()) > 0:
            plt.figure(figsize=(7, 7))
            labels = list(mistakes.keys())
            sizes = list(mistakes.values())
            colors = ['#d3d3d3', '#ff6666', '#ffcc99']
            plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
            plt.title("Error Type Share in Guesser Mistakes")
            plt.savefig(os.path.join(save_dir, "error_types_pie.png"))
            plt.close()

        if hits_per_turn:
            df_turns = pd.DataFrame(hits_per_turn, columns=["Turn", "Hits"])
            avg_hits = df_turns.groupby("Turn")["Hits"].mean().reset_index()

            plt.figure(figsize=(8, 5))
            sns.lineplot(data=avg_hits, x="Turn", y="Hits", marker="o", color='green')
            plt.title("Average Number of Hits per Turn")
            plt.xlabel("Turn Number")
            plt.ylabel("Average Hits")
            plt.xticks(avg_hits["Turn"])
            plt.grid(True, linestyle="--", alpha=0.6)
            plt.savefig(os.path.join(save_dir, "linear_effectiveness_per_turn.png"))
            plt.close()

        print("Charts were successfully generated and saved!")


def main():
    import sys
    import os

    if len(sys.argv) < 2:
        print("Enter the test name")
        return
    test_name = sys.argv[1]
    plots_path=os.path.join("plots", test_name)
    config_source = os.path.join("stats", test_name, "config.yaml")
    config_destination = os.path.join(plots_path, "config.yaml")
    analyzer = ReplayAnalyzer(test_name)

    if len(analyzer.replays_data) > 0:
        analyzer.get_game_stats()
        analyzer.get_spymaster_stats()
        analyzer.get_guesser_stats()
        analyzer.generate_charts(save_dir=plots_path)
        if os.path.exists(config_source):
            shutil.copy(config_source, config_destination)
            print(f"Copied configuration file to: {config_destination}")
        else:
            print(f"Warning: config.yaml not found in {config_source}")
    else:
        print("Cannot perform analysis. Run the game first to generate .pkl.gz files")

# Example usage at the end of the file:
if __name__ == "__main__":
    main()