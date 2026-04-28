import os
import gzip
import pickle
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter


class ReplayAnalyzer:
    def __init__(self, replays_folder: str):
        self.replays_folder = replays_folder
        self.replays_data = []
        self._load_all_replays()

    def _load_all_replays(self):
        """Wczytuje wszystkie pliki powtórek z podanego folderu."""
        search_pattern = os.path.join(self.replays_folder, "*.pkl.gz")
        files = glob.glob(search_pattern)
        print(f"Znaleziono {len(files)} plików powtórek.")

        for file in files:
            try:
                with gzip.open(file, "rb") as f:
                    data = pickle.load(f)
                    self.replays_data.append(data)
            except Exception as e:
                print(f"Błąd podczas wczytywania {file}: {e}")


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

        print(f"Liczba poprawnych podpowiedzi: {total_clues}")
        print(f"Średnia liczba słów na podpowiedź (agresywność): {avg_count:.2f}")
        print(f"Liczba błędnych podpowiedzi (INVALID_CLUE): {invalid_clues}")
        if similarities_list:
            print(f"Średnie podobieństwo (Cosine Similarity) podpowiedzi: {avg_sim:.4f}")

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

        print(f"Całkowita liczba prób strzałów (bez PASS): {total_guesses}")
        print(f"Skuteczność (Trafienia w TARGET): {precision:.2f}%")
        print(f"Ilość pasów (PASS): {passes}")
        print(f"Trafienia w karty NEUTRALNE: {neutral_hits}")
        print(f"Trafienia w ZABÓJCĘ: {assassin_hits}")
        print(f"Nielegalne strzały (INVALID_GUESS): {invalid_guesses}")

        return {
            "precision": precision,
            "passes": passes,
            "neutral_hits": neutral_hits,
            "assassin_hits": assassin_hits,
            "invalid_guesses": invalid_guesses
        }


    def generate_charts(self, save_dir="plots"):
        os.makedirs(save_dir, exist_ok=True)
        print(f"\n--- [D] Generowanie wykresów do folderu: {save_dir} ---")

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
            plt.title("Rozkład Długości Gier (Liczba Tur)")
            plt.xlabel("Liczba Tur")
            plt.ylabel("Liczba Gier")
            plt.savefig(os.path.join(save_dir, "histogram_dlugosci_gier.png"))
            plt.close()

        if sum(mistakes.values()) > 0:
            plt.figure(figsize=(7, 7))
            labels = list(mistakes.keys())
            sizes = list(mistakes.values())
            colors = ['#d3d3d3', '#ff6666', '#ffcc99']
            plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
            plt.title("Udział typów błędów w pomyłkach Guessera")
            plt.savefig(os.path.join(save_dir, "kolowy_pomyki.png"))
            plt.close()

        if hits_per_turn:
            df_turns = pd.DataFrame(hits_per_turn, columns=["Tura", "Trafienia"])
            avg_hits = df_turns.groupby("Tura")["Trafienia"].mean().reset_index()

            plt.figure(figsize=(8, 5))
            sns.lineplot(data=avg_hits, x="Tura", y="Trafienia", marker="o", color="green")
            plt.title("Średnia liczba trafionych celów w danej turze")
            plt.xlabel("Numer Tury")
            plt.ylabel("Średnia liczba trafień")
            plt.xticks(avg_hits["Tura"])
            plt.grid(True, linestyle="--", alpha=0.6)
            plt.savefig(os.path.join(save_dir, "liniowy_skutecznosc_tura.png"))
            plt.close()

        print("Wykresy zostały pomyślnie wygenerowane i zapisane!")


# Przykładowe użycie na końcu pliku:
if __name__ == "__main__":

    analyzer = ReplayAnalyzer(replays_folder="../stats/test-for-stats/replays")

    if len(analyzer.replays_data) > 0:
        analyzer.get_spymaster_stats()
        analyzer.get_guesser_stats()
        analyzer.generate_charts(save_dir="plots")
    else:
        print("Nie można wykonać analizy. Uruchom najpierw grę, aby wygenerować pliki .pkl.gz")