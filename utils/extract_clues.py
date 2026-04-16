import gzip
import pickle
import glob
import os


def extract_clues_to_txt(replays_dir: str, output_txt: str):

    replay_files = glob.glob(os.path.join(replays_dir, "**/*.pkl.gz"), recursive=True)

    if not replay_files:
        print(f"Nie znaleziono plików .pkl.gz w folderze: {replays_dir}")
        return

    seen_lines = set()
    with open(output_txt, "w", encoding="utf-8") as out_f:
        for file in replay_files:
            try:

                with gzip.open(file, "rb") as f:
                    data = pickle.load(f)

                history = data.get("history", [])


                for event in history:
                    if event.get("action") == "CLUE":
                        clue = event.get("clue", "Brak")
                        words = event.get("words", [])
                        similarities = event.get("similarities")
                        if similarities and len(words) == len(similarities):
                            words_with_sim = [f"{w} ({sim:.3f})" for w, sim in zip(words, similarities)]
                            line = f'Clue = "{clue}", Mean = {words_with_sim}\n'
                        else:
                            line = f'Clue = "{clue}", Mean = {words}\n'




                        if line not in seen_lines:
                            out_f.write(line)
                            seen_lines.add(line)

            except Exception as e:
                print(f"Błąd podczas przetwarzania pliku {file}: {e}")

    print(f"Zakończono! Zapisano {len(seen_lines)} unikalnych haseł z {len(replay_files)} plików do {output_txt}")


if __name__ == "__main__":
    Katalog_Z_Logami = "../stats/test"
    Plik_Wyjsciowy = "wyciagniete_hasla.txt"

    extract_clues_to_txt(Katalog_Z_Logami, Plik_Wyjsciowy)