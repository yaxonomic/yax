from yax.state.type import Artifact
import os


class ArtifactB(Artifact):
    def __init__(self, completed):
        self.number_int = None

        if completed:
            self.read_text()

    def read_text(self):
        with open(os.path.join(self.data_dir, "artifact_b.txt"), 'r') as fh:
            _, self.number_int = fh.read().splitlines()
        self.number_int = int(self.number_int)

    def __complete__(self):
        with open(os.path.join(self.data_dir, "artifact_b.txt"), 'w') as fh:
            fh.write("\n".join([self.module_id, str(self.number_int)]))
