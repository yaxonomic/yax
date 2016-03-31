from yax.state.tests.test_pipeline.artifacts.artifact_c import ArtifactC
from yax.state.type.parameter import Str


def main(working_dir, output, input_str: Str) -> ArtifactC:
    art_c = output

    art_c.text = input_str

    with open("".join([working_dir, "module_2.txt"]), 'w') as fh:
        fh.write("module_2")

    return output
