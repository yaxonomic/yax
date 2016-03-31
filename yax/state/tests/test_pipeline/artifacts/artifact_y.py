from yax.state.type import Artifact


class ArtifactY(Artifact):
    final_user_output = True

    def __init__(self, completed):
        self.text = None
        self.number_float = None
        self.number_int = None
        self.boolean_val = None

        if completed:
            self.read_text()

    def read_text(self):
        with open("".join([self.data_dir, "artifact_b.txt"]), 'r') as fh:
                artifact_lines = fh.read().splitlines()

        self.text = artifact_lines[1]
        self.number_int = 0
        for line in artifact_lines:
            if line is self.text:
                self.number_int += 1

        self.number_float = float(artifact_lines[-1])

    def __complete__(self):
        with open("".join([self.data_dir, "artifact_b.txt"]), 'w') as fh:
            fh.write("\n".join([self.module_id, self.text * self.number_int,
                                str(self.number_float),
                                str(self.boolean_val)]))
