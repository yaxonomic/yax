import os.path
import sqlite3

class ArtifactMap:
    def __init__(self, db_fp, exe_graph):
        db_exists = os.path.isfile(db_fp)

        self.graph = exe_graph
        self.conn = sqlite3.connect(db_fp)

        if not db_exists:
            self._init_database()

    def _init_database(self):
        pass
