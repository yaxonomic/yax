from yax.state.type import Str
from .artifacts import MyArtifact, MyOtherArtifact, MyInputArtifact


def main(output: (MyArtifact, MyOtherArtifact), param1: Str, param2: Str,
         extra: MyInputArtifact):
    return 1, 2
