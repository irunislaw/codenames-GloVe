import os
import gzip
import pickle
import glob
from collections import Counter, defaultdict


class AdvancedReplayAnalyzer:
    def __init__(self, replays_folder: str):
        self.replays_folder = replays_folder
        self.replays_data = []
        self._load_all_replays()

    def _load_all_replays(self):
        files = glob.glob(os.path.join(self.replays_folder, "*.pkl.gz"))
        for file in files:
            with gzip.open(file, "rb") as f:
                self.replays_data.append(pickle.load(f))
        print(f"Loaded {len(self.replays_data)} replays for advanced analysis.")

    def run_advanced_analytics(self):

        misaligned_guesses = 0  # Guesser strzela w słowa, których Spymaster nie podał
        aligned_guesses = 0  # Guesser strzela w to, o czym myślał Spymaster
        wasted_clues = 0  # Słowa uciekające z winy Guessera (Spymaster daje 3, Guesser zgaduje 1 i pasuje)
        bonus_n_plus_one_used = 0  # Guesser zgaduje N+1 razy


        spymaster_vocab = set()


        blacklisted_words = Counter()


        games_with_early_mistake = 0
        early_mistakes_recovered = 0  # Wygrane po błędzie w 1/2 turze


        spymaster_times = []
        guesser_times = []

        for game in self.replays_data:
            history = game.get("history", [])
            initial_board = game.get("initial_board", [])


            current_clue_targets = []
            current_clue_count = 0
            guesses_in_this_turn = 0
            correct_guesses_in_this_turn = 0
            turn_number = 0
            early_mistake_made = False
            is_victory = False

            for event in history:
                action = event.get("action")


                if "latency" in event:
                    if action == "CLUE":
                        spymaster_times.append(event["latency"])
                    elif action == "GUESS":
                        guesser_times.append(event["latency"])

                if action == "CLUE":
                    turn_number += 1
                    spymaster_vocab.add(event.get("clue"))
                    current_clue_targets = event.get("words", [])
                    current_clue_count = event.get("count", 0)
                    guesses_in_this_turn = 0
                    correct_guesses_in_this_turn = 0

                elif action == "GUESS":
                    word = event.get("word")
                    result = event.get("result")

                    if word != "PASS":
                        guesses_in_this_turn += 1


                        if current_clue_targets and word in current_clue_targets:
                            aligned_guesses += 1
                        elif current_clue_targets:
                            misaligned_guesses += 1


                        if result != "TARGET":
                            blacklisted_words[word] += 1
                            if turn_number <= 2:
                                early_mistake_made = True
                        else:
                            correct_guesses_in_this_turn += 1


                    if word == "PASS" or result in ["NEUTRAL", "ASSASSIN"]:

                        if correct_guesses_in_this_turn < current_clue_count:
                            wasted_clues += (current_clue_count - correct_guesses_in_this_turn)

                        if result == "ASSASSIN":
                            is_victory = False

                    if guesses_in_this_turn > current_clue_count and result == "TARGET":
                        bonus_n_plus_one_used += 1


            targets_left = history[-1].get("score_left", 9) if history else 9
            if targets_left == 0 and history[-1].get("result") != "ASSASSIN":
                is_victory = True

            if early_mistake_made:
                games_with_early_mistake += 1
                if is_victory:
                    early_mistakes_recovered += 1

        self._print_report(aligned_guesses, misaligned_guesses, wasted_clues, bonus_n_plus_one_used,
                           spymaster_vocab, spymaster_times, guesser_times,
                           games_with_early_mistake, early_mistakes_recovered, blacklisted_words)

    def _print_report(self, aligned, misaligned, wasted, bonus, vocab, s_times, g_times, early_mistake, recovered,
                      blacklist):
        print("\n" + "=" * 50)
        print("  RAPORT ZAAWANSOWANEJ ANALIZY NLP / GAMEPLAY  ")
        print("=" * 50)


        total_intent_guesses = aligned + misaligned
        misalignment_rate = (misaligned / total_intent_guesses * 100) if total_intent_guesses > 0 else 0
        print("\n--- 1. UNDERSTANDING METRICS ---")
        print(f"Misalignment Rate: {misalignment_rate:.1f}%")
        print(f"Wasted clue potential (Wasted Clues): {wasted} words")
        print(f"Bonus Guesses used: {bonus} times")


        print("\n--- 2. LEXICAL RICHNESS ---")
        print(f"Vocabulary diversity (Unique clues): {len(vocab)} words")


        recovery_rate = (recovered / early_mistake * 100) if early_mistake > 0 else 0
        print("\n--- 3. GAME MOMENTUM ---")
        print(
            f"Recovery rate after an early mistake: {recovery_rate:.1f}% ({recovered}/{early_mistake} games)")


        avg_s = sum(s_times) / len(s_times) if s_times else 0
        avg_g = sum(g_times) / len(g_times) if g_times else 0
        print("\n--- 4. AVERAGE PROCESSING TIME (LATENCY) ---")
        print(f"Spymaster: {avg_s:.2f} s / turn")
        print(f"Guesser:   {avg_g:.2f} s / turn")


        print("\n--- 5. BLACKLIST (Most deceptive words) ---")
        for word, count in blacklist.most_common(5):
            print(f"  - '{word}': missed {count} times")
        print("=" * 50 + "\n")


if __name__ == "__main__":
    import sys 
    import os

    test_name = sys.argv[1] if len(sys.argv) > 1 else None
    if test_name is None:
        print("Provide the test name as an argument (e.g. 'test1')")
        exit(1)
    analyzer = AdvancedReplayAnalyzer(os.path.join("stats", test_name, "replays"))
    analyzer.run_advanced_analytics()