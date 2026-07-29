from config import settings

from players.glove_spymaster import GloveSpyMaster
from players.history_glove_spymaster import HistoryGloveSpyMaster

def prepare_spymaster(logger=None):
    spymaster = None
    type = settings["glove_spymaster"]["type"]

    if type == "history":
        # print("[SPYMASTER]: creating history spymaster")
        spymaster = HistoryGloveSpyMaster(
                    weight_assassin=settings["glove_spymaster"]["weight_assassin"],
                    weight_neutral=settings["glove_spymaster"]["weight_neutral"],
                    word_bonus=settings["glove_spymaster"]["word_bonus"],
                    number_targets=settings["glove_spymaster"]["number_targets"],
                    clue_validation=settings["glove_spymaster"]["clue_validation"],
                    time_limit=settings["glove_spymaster"]["time_limit"],
                    logger=logger
                ) 
    else:
        # default normal
        # print("[SPYMASTER]: creating normal spymaster")
        spymaster = GloveSpyMaster(
                    weight_assassin=settings["glove_spymaster"]["weight_assassin"],
                    weight_neutral=settings["glove_spymaster"]["weight_neutral"],
                    word_bonus=settings["glove_spymaster"]["word_bonus"],
                    number_targets=settings["glove_spymaster"]["number_targets"],
                    clue_validation=settings["glove_spymaster"]["clue_validation"],
                    time_limit=settings["glove_spymaster"]["time_limit"],
                    logger=logger
                ) 
    return spymaster

print(f"[PREP_SPYMASTER] config type: {settings["glove_spymaster"]["type"]}")
