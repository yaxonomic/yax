from yax.state.tests.test_pipeline.artifacts.artifact_a import ArtifactA
from yax.state.tests.test_pipeline.artifacts.artifact_b import ArtifactB
from yax.state.type.parameter import Float, Int
import os


def main(working_dir, output, details, input_float: Float, input_int: Int)\
        -> (ArtifactA, ArtifactB):
    art_a, art_b = output

    art_a.number_float = input_float
    art_b.number_int = input_int

    with open(os.path.join(working_dir, "module_1.txt"), 'w') as fh:
        fh.write("module_1")

    return output
