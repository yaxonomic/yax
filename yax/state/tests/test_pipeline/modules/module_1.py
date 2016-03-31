from ..artifacts.artifact_a import ArtifactA
from ..artifacts.artifact_b import ArtifactB
from state.type.parameter import Float, Int


def main(working_dir, output, input_float: Float, input_int: Int)\
        -> (ArtifactA, ArtifactB):
    art_a, art_b = output

    art_a.number_float = input_float
    art_b.number_int = input_int

    with open("".join([working_dir, "module_1.txt"]), 'w') as fh:
        fh.write("module_1")

    return output
