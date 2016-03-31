from yax.state.type import Artifact


class ArtifactB(Artifact):
    def __init__(self, completed):
        self.number_int = None

        if completed:
            self.read_text()

    def read_text(self):
        with open("".join([self.data_dir, "artifact_b.txt"]), 'r') as fh:
                _, self.number_int = fh.read().splitlines()

    def __complete__(self):
        with open("".join([self.data_dir, "artifact_b.txt"]), 'w') as fh:
            fh.write("\n".join([self.module_id, self.number_int]))
