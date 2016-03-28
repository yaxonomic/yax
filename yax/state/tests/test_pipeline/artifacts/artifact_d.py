from state.type import Artifact


class ArtifactD(Artifact):
    def __init__(self, completed):
        self.text_from_file = None

        if completed:
            self.read_file()

    def read_file(self):
        with open("".join([self.data_dir, "artifact_d.txt"]), 'r') as fh:
                _, self.text_from_file = fh.read().splitlines()

    def __complete__(self):
        with open("".join([self.data_dir, "artifact_d.txt"]), 'w') as fh:
            fh.write("\n".join([self.module_id, self.text_from_file]))