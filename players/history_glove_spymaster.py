from glove_spymaster import GloveSpyMaster
import numpy as np

class HistoryGloveSpyMaster(GloveSpyMaster):
    def __init__(self, **kwargs):
        # 3D array
        # number of words clue is targeting, number of guessed words, number of words 
        self.table = np.zeros(shape=(9, 9, 9))
        super().__init__(**kwargs)