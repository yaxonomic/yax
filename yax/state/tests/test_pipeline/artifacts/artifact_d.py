from state.type import Artifact


class ArtifactD(Artifact):
    def __init__(self, completed):
        self.text = None
        self.number_int = None
        self.file_text = None

        if completed:
            self.read_file()

    def read_file(self):
        with open("".join([self.data_dir, "artifact_d.txt"]), 'r') as fh:
                art_lines = fh.read().splitlines()

        art_lines = art_lines[1:]
        self.text = art_lines[0]
        self.number_int = int(len(art_lines))

    def __complete__(self):
        with open("".join([self.data_dir, "artifact_d.txt"]), 'w') as fh:
            fh.write("\n".join([self.module_id, self.text * self.number_int,
                                self.file_text]))