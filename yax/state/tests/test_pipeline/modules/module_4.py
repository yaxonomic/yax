from yax.state.tests.test_pipeline.artifacts.artifact_a import ArtifactA
from yax.state.tests.test_pipeline.artifacts.artifact_d import ArtifactD
from yax.state.tests.test_pipeline.artifacts.artifact_y import ArtifactY
from yax.state.type import Directory, Float
import os


def main(working_dir, output, details, art_a: ArtifactA, art_d: ArtifactD,
         input_dir: Directory, input_default_float: Float=11.1) -> ArtifactY:
    art_y, = output

    art_y.number_int = art_d.number_int
    art_y.number_float = art_a.number_float
    art_y.text = art_d.text

    if art_a.number_float > input_default_float:
        art_y.boolean_val = True

    with open(os.path.join(input_dir, "test.txt"), 'w') as fh:
        fh.write("Module 4 test")

    with open(os.path.join(working_dir, "module_2.txt"), 'w') as fh:
        fh.write("module_2")

    return output
