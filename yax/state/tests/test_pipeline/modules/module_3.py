from ..artifacts.artifact_b import ArtifactB
from ..artifacts.artifact_c import ArtifactC
from ..artifacts.artifact_d import ArtifactD
from state.type.parameter import Str, Int, File


def main(working_dir, output, art_b: ArtifactB, art_c: ArtifactC,
         input_file: File) -> ArtifactD:
    art_d = output

    art_d.number_int = art_b.number_int
    art_d.text = art_c.text

    with open(input_file, 'r') as fh:
        art_d.file_text = fh.readline()

    with open("".join([working_dir, "module_2.txt"]), 'w') as fh:
        fh.write("module_2")

    return output
