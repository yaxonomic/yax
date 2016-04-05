from yax.state.type import Artifact


class IdentifiedTaxa(Artifact):
    def __init__(self, completed):
        self.identified_taxa_file = None

        if completed:
            self.identified_taxa_file = None
            self.read_identified_taxa()

    def read_identified_taxa():
        pass

    def __complete__(self):
        pass
