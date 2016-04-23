from yax.state.tests.test_pipeline.artifacts.artifact_b import ArtifactB
from yax.state.tests.test_pipeline.artifacts.artifact_c import ArtifactC
from yax.state.tests.test_pipeline.artifacts.artifact_d import ArtifactD
from yax.state.type.parameter import File


def main(working_dir, output, details, art_b: ArtifactB, art_c: ArtifactC,
         input_file: File) -> ArtifactD:
    art_d = output

    art_d.number_int = art_b.number_int
    art_d.text = art_c.text

    with open(input_file, 'r') as fh:
        art_d.file_text = fh.readline()

    with open("".join([working_dir, "module_2.txt"]), 'w') as fh:
        fh.write("module_2")

    return output
