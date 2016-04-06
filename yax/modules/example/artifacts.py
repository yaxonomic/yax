from yax.state.type import Artifact


# example of init which could be used to identify a completed artifact and
# artifact values from it or create an empty artifact and values to operate on
#
# def __init__(self, completed):
#         self.plain_text_output = None
#
#         if completed:
#             self.read_text()

class MyArtifact(Artifact):
    pass


class MyOtherArtifact(Artifact):
    pass


class MyInputArtifact(Artifact):
    pass
