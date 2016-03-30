from ..artifacts.artifact_a import ArtifactA
from ..artifacts.artifact_d import ArtifactD
from ..artifacts.artifact_y import ArtifactY
from state.type.parameter import Directory


def main(working_dir, output, art_a: ArtifactA, art_d: ArtifactD,
         input_dir: Directory) -> ArtifactY:
    art_y = output

    art_y.number_int = art_d.number_int
    art_y.number_float = art_a.number_float
    art_y.text = art_d.text

    with open("".join([input_dir, "test.txt"]), 'w') as fh:
        fh.write("Module 4 test")

    with open("".join([working_dir, "module_2.txt"]), 'w') as fh:
        fh.write("module_2")

    art_y.complete()
