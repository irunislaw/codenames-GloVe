import gzip
import pickle
import glob
import os


def extract_clues_to_txt(replays_dir: str, output_txt: str):

    replay_files = glob.glob(os.path.join(replays_dir, "**/*.pkl.gz"), recursive=True)

    if not replay_files:
        print(f"No .pkl.gz files found in folder: {replays_dir}")
        return

    seen_lines = set()
    os.makedirs(os.path.dirname(output_txt) or ".", exist_ok=True)
    with open(output_txt, "w", encoding="utf-8") as out_f:
        for file in replay_files:
            try:

                with gzip.open(file, "rb") as f:
                    data = pickle.load(f)

                history = data.get("history", [])


                for event in history:
                    if event.get("action") == "CLUE":
                        clue = event.get("clue", "None")
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
                print(f"Error processing file {file}: {e}")

    print(f"Done! Saved {len(seen_lines)} unique clues from {len(replay_files)} files to {output_txt}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python extract_clues.py <batch_name>")
        print("Example: python extract_clues.py test")
        sys.exit(1)

    batch_name = sys.argv[1]
    replays_dir = os.path.join("stats", batch_name, "replays")
    output_txt = os.path.join("stats", batch_name, "extracted_clues.txt")

    extract_clues_to_txt(replays_dir, output_txt)