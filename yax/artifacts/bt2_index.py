from yax.state.type import Artifact

import os

class BT2Index(Artifact):
    def __init__(self, completed):
        self.index_files = os.path.join(self.data_dir, "/index")
