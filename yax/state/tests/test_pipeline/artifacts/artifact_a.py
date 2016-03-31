from yax.state.type import Artifact


class ArtifactA(Artifact):
    def __init__(self, completed):
        self.number_float = None

        if completed:
            self.read_math()

    def read_math(self):
        with open("".join([self.data_dir, "artifact_a.txt"]), 'r') as fh:
                _, self.number_float = fh.read().splitlines()

    def __complete__(self):
        with open("".join([self.data_dir, "artifact_a.txt"]), 'w') as fh:
            fh.write("\n".join([self.module_id, self.number_float]))
