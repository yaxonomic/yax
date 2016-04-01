from yax.state.type import Str
from .artifacts import MyArtifact, MyOtherArtifact, MyInputArtifact


def main(working_dir, output, param1: Str, param2: Str,
         extra: MyInputArtifact) -> (MyArtifact, MyOtherArtifact):
    return 1, 2
