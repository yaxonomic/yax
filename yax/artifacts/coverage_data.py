from yax.state.type import Artifact


class CoverageData(Artifact):

    def __init__(self):
        super().__init__(self)
        self.samples = []

    def __complete__(self):
        self.samples = []

    class Sample:
        def __init__(self, name):
            self.name = name
            self.sequences = []
            self.alignments = []

    class Sequence:
        def __init__(self, gi, length):
            self.gi = gi
            self.length = length

    class Alignment:
        def __init__(self, gi, length, position):
            self.gi = gi
            self.length = length
            self.position = position
