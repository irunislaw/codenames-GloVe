import json
import os
import random

from game.codenames import Codenames, CardType, Card


class DatasetManager:
    @staticmethod
    def generate_and_save_dataset(words_pool: list, num_boards: int, filepath: str, target_count: int = 9):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        dataset = []
        for i in range(num_boards):
            temp_game = Codenames(words=random.sample(words_pool, 25), target_count=target_count)
            board_data = [{"word": c.word,"type": c.card_type.value} for c in temp_game.board ]
            dataset.append({"board_id": i, "board": board_data})

        with open(filepath,'w',encoding='utf-8') as f:
            json.dump(dataset,f,ensure_ascii=False,indent=2)
        print(f"Dataset of {num_boards} boards saved to {filepath}")

    @staticmethod
    def load_dataset(filepath: str)-> list[tuple[int,list[Card]]]:
        with open(filepath,'r',encoding='utf-8') as f:
            dataset = json.load(f)
        boards = []
        for item in dataset:
            board = [Card(word =c["word"], card_type=CardType(c["type"])) for c in item["board"]]
            boards.append((item["board_id"],board))
        return boards

    #TODO ZEBY WSZEDZZIE POKAZYWALO TYPY ZWRACANE I WGL

