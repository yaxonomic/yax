import os

from yax.state.type import Artifact


class PreparedReads(Artifact):
    def __init__(self, completed):
        self.config_file_fp = None
        self.prepared_reads_fp = None

    def __complete__(self):
        os.remove(self.config_file_fp)
