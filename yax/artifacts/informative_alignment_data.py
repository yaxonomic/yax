from yax.state.type.artifact import Artifact
from yax.shared.utilities import taxidtool


class InformativeAlignmentData(Artifact):
    def __init__(self, completed):
        self.tax_id_data = None
        self.inclusion_tree = None
        self.gis_to_taxids = None
        self.sequences_input_fp = None
        self.truncation_level = None

        if completed:
            pass

    def __complete__(self):
        taxidtool.output_tree(self.taxid_data, self.inclusion_tree,
                              self.data_dir)
        taxidtool.output_sequences(self.taxid_data, self.inclusion_tree,
                                   self.gis_to_taxids, self.sequences_input_fp,
                                   self.data_dir, self.truncation_level)
