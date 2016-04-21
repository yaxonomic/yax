from yax.state.type import Artifact
import os


class ArtifactX(Artifact):
    final_user_output = True

    def __init__(self, completed):
        self.text = None

        if completed:
            self.read_text()

    def read_text(self):
        with open(os.path.join(self.data_dir, "artifact_x.txt"), 'r') as fh:
            _, self.text = fh.read().splitlines()

    def __complete__(self):
        with open(os.path.join(self.data_dir, "artifact_x.txt"), 'w') as fh:
            fh.write("\n".join([self.module_id, self.text]))
