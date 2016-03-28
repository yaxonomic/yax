from ..artifacts.artifact_a import ArtifactA
from ..artifacts.artifact_b import ArtifactB
from state.type.parameter import Float, Int, Str


def main(_, output, example_float: Float, example_int: Int)\
        -> (ArtifactA, ArtifactB):
    art_a, art_b = output
    art_a.math_output = do_math(example_float, example_int)
    art_a.complete()


def do_math(self, a, b):
    output = (a * b) % a
    return output